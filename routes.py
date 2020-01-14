"""
License information goes here.
"""

import os

from starp import Starp
from starp.exceptions import StarpError
from nestedloop import NestedLoop
from nestedloop import NestedLoopError

from flask import Flask, Response, render_template, redirect, session, request
from flask_session import Session

from forms import StarpForm, NestedLoopForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
""" By default, a maximum 500 sessions are stored at once. """
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def go_to_homepage():
    """ By default, send the user to the starp page. """
    return redirect('/starp')

@app.route('/starp')
def show_form():
    """ Display the Starp form with default values. """
    form = StarpForm()
    return render_template('/starp.html', form=form)

@app.route('/starp', methods=['POST'])
def starp_post():
    """ The user has submitted some action. If they've just clicked
    submit, move them to the next stage to select the SNP. If they've
    chosen the SNP, compute primers. """
    form = StarpForm()

    if 'snp' in request.form:
        # User has chosen their SNP. Compute primers.
        chosen_snp_descriptor = request.form['snp']
        session['starp'].set_snp(chosen_snp_descriptor)
        try:
            session['starp'].run()
        except StarpError as e:
            form.errors['starp'] = [e.message]
            return render_template('starp.html', form=form)
        return render_template('starp.html', form=form, starp=session['starp'])

    # User has submitted the initial data. Find the SNPS, and ask the
    # user which one to design primers around.
    try:
        starp = Starp(form.input_data.data)
        session['starp'] = starp
        snp_gui = starp.html()
    except StarpError as e:
        form.errors['starp'] = [e.message]
        return render_template('starp.html', form=form)
    return render_template('starp.html', form=form, snp_gui=snp_gui)

@app.route('/nestedloop')
def go_to_nestedloop():
    """ Display the Nested Loop form with default values. """
    form = NestedLoopForm()
    return render_template('/nestedloop.html', form=form)

@app.route('/nestedloop', methods=['POST'])
def create_pairs():
    """ Compute primers based off the user's supplied information. """
    form = NestedLoopForm()
    if not form.validate_on_submit():
        return render_template('nestedloop.html', form=form)

    session['nl'] = NestedLoop(form.ref_sequence.data,
                               (form.tm_min.data, form.tm_opt.data, form.tm_max.data),
                               form.f_from.data,
                               form.f_to.data,
                               form.r_from.data,
                               form.r_to.data,
                               form.pcr_min.data,
                               form.pcr_max.data,
                               form.num_to_return.data,
                               form.forward_primer.data,
                               form.reverse_primer.data,
                               form.non_targets.data)

    try:
        session['nl'].run()
        #session['nl'].create_pairs()
    except NestedLoopError as e:
        form.errors["NL"] = [e.message]
        return render_template('nestedloop.html', **locals())

    return render_template('nestedloop.html', form=form, pairs=session['nl'].pairs)

@app.route('/downloadCSV')
def download_csv():
    """ Send the user's results as a csv file. """
    nl = session['nl']
    csv = ("#,Type,Sequence (5'->3'),Strand,Start,End,Tm (Celsius),"
           "GC Content,Amplicon Length,Additive,Loop 2 Program,"
           "Loop 2 Cycle Number\n")
    csv += "\n"
    pair_number = 1
    for pair in nl.pairs:
        pair_csv = (f'{str(pair_number)},Forward,{pair.forward_primer.sequence},'
                    f'Plus,{str(pair.forward_primer.start)},'
                    f'{str(pair.forward_primer.end)},'
                    f'{str(pair.forward_primer.tm)},'
                    f'{str(pair.forward_primer.gc)},'
                    f'{str(pair.distance)},{pair.additive().additive},'
                    + pair.additive().pcr_temperatures.replace("\n", " ") +
                    f',{str(pair.additive().n)}' + '\n')

        pair_csv += (f',Reverse,{pair.reverse_primer.sequence},Minus,'
                     f'{str(pair.reverse_primer.start)},'
                     f'{str(pair.reverse_primer.end)},'
                     f'{str(pair.reverse_primer.tm)},'
                     f'{str(pair.reverse_primer.gc)}' + '\n\n')

        csv += pair_csv
        pair_number += 1

    return Response(csv,
                    mimetype="text/csv",
                    headers={"Content-disposition":
                             "attachment; filename=primers.csv"})

if __name__ == "__main__":
    app.run(debug=True)
