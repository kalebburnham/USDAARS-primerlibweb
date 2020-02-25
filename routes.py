"""
License information goes here.
"""

import os
import json

from starp import Starp
from starp.exceptions import StarpError
from nestedloop import NestedLoop
from nestedloop.exceptions import NestedLoopError

from flask import Flask, Response, render_template, redirect, session, request, jsonify, url_for

app = Flask(__name__, template_folder='primerlibweb/templates')
app.secret_key = 'OD jhfSD :FHFIOKL: NFEWnk448299'

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)

@app.route('/')
def go_to_homepage():
    """ By default, send the user to the starp page. """
    return redirect(url_for('starp'))

@app.route('/starp')
def starp():
    """ Display the Starp form with default values. """
    session.clear()
    return render_template('/starp.html')

@app.route('/starp', methods=['POST'])
def starp_post():
    """ The user has submitted some action. If they've just clicked
    submit, move them to the next stage to select the SNP. If they've
    chosen the SNP, compute primers. """
    errors = []

    if 'snp' in request.form:
        # User has chosen their SNP. Compute primers.
        chosen_snp_descriptor = request.form['snp']
        starp = Starp(request.form['input_data'], request.form['non_targets'])
        #starp = Starp(*session['starp'].values())

        try:
            starp = Starp(request.form['input_data'], request.form['non_targets'])
            starp.run()
        except StarpError as e:
            errors.append(e.message)
            return render_template('starp.html', errors=errors,
                                   sequence_data=request.form['input_data'],
                                   nontargets=request.form['non_targets'])
        except ValueError as e:
            errors.append(e)
            return render_template('starp.html', errors=errors,
                                   sequence_data=request.form['input_data'],
                                   nontargets=request.form['non_targets'])

        return render_template('starpresults.html',
                               sequence_data=request.form['input_data'],
                               nontargets=request.form['non_targets'],
                               starp=starp)


    try:
        starp = Starp(request.form['input_data'])
        starp.run()
    except StarpError as e:
        errors.append(e.message)
        return render_template('starp.html', errors=errors,
                               sequence_data=request.form['input_data'],
                               nontargets=request.form['non_targets'])
    except ValueError as e:
        errors.append(e)
        return render_template('starp.html', errors=errors,
                               sequence_data=request.form['input_data'],
                               nontargets=request.form['non_targets'])

    return render_template('starpresults.html', starp=starp)

@app.route('/nestedloop')
def nestedloop():
    """ Display the Nested Loop form with default values. """
    session.clear()
    return render_template('/nestedloop.html')

@app.route('/nestedloop', methods=['POST'])
def run_nestedloop():
    """ Compute primers based off the user's supplied information. """


    # Sequence data may be too large to store as a session variable,
    # so it cannot be included here.
    session['tm'] = {'min': float(request.form['tm_min']),
                     'opt': float(request.form['tm_opt']),
                     'max': float(request.form['tm_max'])}
    session['f_from'] = int(request.form['fFrom'])
    session['f_to'] = int(request.form['fTo'])
    session['r_from'] = int(request.form['rFrom'])
    session['r_to'] = int(request.form['rTo'])
    session['pcr_min'] = int(request.form['pcr_min'])
    session['pcr_max'] = int(request.form['pcr_max'])
    session['num_to_return'] = int(request.form['num_to_return'])
    session['forward_primer'] = request.form['forward_primer']
    session['reverse_primer'] = request.form['reverse_primer']
    
    errors = []
    try:
        nl = NestedLoop(ref_sequence=request.form['ref_sequence'],
                    tm=(session['tm']['min'], session['tm']['opt'], session['tm']['max']),
                    f_from=session['f_from'],
                    f_to=session['f_to'],
                    r_from=session['r_from'],
                    r_to=session['r_to'],
                    pcr_min=session['pcr_min'],
                    pcr_max=session['pcr_max'],
                    num_to_return=session['num_to_return'],
                    custom_forward_primer=session['forward_primer'],
                    custom_reverse_primer=session['reverse_primer'],
                    nontargets=request.form['non_targets'])

        nl.run()
        #session['nl'].create_pairs()
        session['pairs'] = [pair.toJSON() for pair in nl.pairs]
    except NestedLoopError as e:
        errors.append(e.message)
        return render_template('nestedloop.html', session=session,
                               errors=errors, ref_sequence=request.form['ref_sequence'],
                               nontargets=request.form['non_targets'])
    except ValueError as e:
        errors.append(e)
        return render_template('nestedloop.html', session=session,
                               errors=errors, ref_sequence=request.form['ref_sequence'],
                               nontargets=request.form['non_targets'])
    """ For production
    except Exception as e:
        errors.append(e)
        errors.append("Something went wrong. Please try again.")
        return render_template('nestedloop.html', session=session,
                               errors=errors, ref_sequence=request.form['ref_sequence'],
                               nontargets=request.form['non_targets'])
    """

    return render_template('nestedloop.html', session=session, 
                           ref_sequence=request.form['ref_sequence'],
                           nontargets=request.form['non_targets'],
                           pairs=nl.pairs)

@app.route('/downloadCSV', methods=['POST'])
def download_csv():
    """ Send the user's results as a csv file. """

    csv = ("#,Type,Sequence (5'->3'),Strand,Start,End,Tm (Celsius),"
           "GC Content,Amplicon Length,Additive,Loop 2 Program,"
           "Loop 2 Cycle Number\n")
    csv += "\n"
    pair_number = 1
    for pair in session['pairs']:

        pair_csv = (f'{str(pair_number)},Forward,{pair["forward_primer"]["sequence"]},'
                        f'Plus,{str(pair["forward_primer"]["span"][0])},'
                        f'{str(pair["forward_primer"]["span"][1])},'
                        f'{str(pair["forward_primer"]["tm"])},'
                        f'{str(pair["forward_primer"]["gc"])},'
                        f'{str(pair["distance"])},{pair["additive"]},'
                        + pair["pcr_temperatures"].replace("\n", " ") +
                        f',{str(pair["n"])}' + '\n')

        pair_csv += (f',Reverse,{pair["reverse_primer"]["sequence"]},Minus,'
                     f'{str(pair["reverse_primer"]["span"][0])},'
                     f'{str(pair["reverse_primer"]["span"][1])},'
                     f'{str(pair["reverse_primer"]["tm"])},'
                     f'{str(pair["reverse_primer"]["gc"])}' + '\n\n')
        

        csv += pair_csv
        pair_number += 1

    return Response(csv,
                    mimetype="text/csv",
                    headers={"Content-disposition":
                             "attachment; filename=primers.csv"})

if __name__ == "__main__":
    app.run(debug=True)
