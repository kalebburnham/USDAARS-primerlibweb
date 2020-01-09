import sys
import os

from flask import Flask, render_template, redirect, session, request
from forms import StarpForm, NestedLoopForm
from flask_session import Session

from starp import Starp
from starp.exceptions import StarpError

from nestedloop import NestedLoop
from nestedloop import NestedLoopError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
""" By default, a maximum 500 sessions are stored at once. """
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def go_to_homepage():
    return redirect('/starp')

@app.route('/starp')
def show_form():
    form = StarpForm()
    return render_template('/starp.html', form=form)

@app.route('/starp', methods=['POST'])
def starp_post():
    form = StarpForm()

    if 'snp' in request.form:
        """ User has chosen their SNP. Compute primers. """
        chosen_snp_descriptor = request.form['snp']
        snp = next((x for x in session['starp'].snps 
            if x.descriptor == chosen_snp_descriptor), None)
        try:
            session['starp'].choose_snp(snp)
        except StarpError as e:
            form.errors['starp'] = [e.message]
            return render_template('starp.html', form=form)
        return render_template('starp.html', form=form, starp=session['starp'])
    else:
        """ User has submitted the initial data. Find the SNPS, and ask
        the user which one to design primers around. """
        try:
            starp = Starp2(form.input_data.data)
            session['starp'] = starp
            snp_gui = starp.html()
        except StarpError as e:
            form.errors['starp'] = [e.message]
            return render_template('starp.html', form=form)
        return render_template('starp.html', form=form, snp_gui=snp_gui)

@app.route('/nestedloop')
def go_to_nestedloop():
    form = NestedLoopForm()
    return render_template('/nestedloop.html', form=form)

@app.route('/nestedloop', methods=['POST'])
def create_pairs():
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

    pairs = session['nl'].pairs
    nl = session['nl']
    return render_template('nestedloop.html', form=form, pairs=pairs)

@app.route('/downloadCSV')
def download_csv():
    nl = session['nl']
    csv = "#,Type,Sequence (5'->3'),Strand,Start,End,Tm (Celsius),GC Content,Amplicon Length,Additive,Loop 2 Program,Loop 2 Cycle Number\n"
    csv += "\n"
    number = 1
    for pair in nl.pairs:
        pair_csv = (str(number) + ',Forward,' + pair.forward_primer.sequence + ',Plus,' + str(pair.forward_primer.start) + ',' + str(pair.forward_primer.end) + ','
                        + str(pair.forward_primer.tm) + ',' + str(pair.forward_primer.gc) + ',' + str(pair.distance) + ',' 
                        + pair.additive().additive + ',' + pair.additive().pcr_temperatures.replace('\n', ' ') + ',' + str(pair.additive().n) + '\n')
        pair_csv += (',Reverse,' + pair.reverse_primer.sequence + ',Minus,' + str(pair.reverse_primer.start) + ',' + str(pair.reverse_primer.end)
                        + ',' + str(pair.reverse_primer.tm) + ',' + str(pair.reverse_primer.gc) + '\n\n')
        csv += pair_csv
        number += 1

    return Response(csv, 
                    mimetype="text/csv", 
                    headers = {"Content-disposition":
                               "attachment; filename=primers.csv"})

if __name__ == "__main__":
    #sys.path.append('./starp')
    app.run(debug=True)
