import google.generativeai as genai
import os
from datetime import date
import nbformat as nbf
import re

genai.configure(api_key=open('apikey.txt').read())
model = genai.GenerativeModel('gemini-pro')


def createReport(console_log, specified_outcome, outcome_line,
                 output_name=('auto_console_report_' + str(date.today()) + '.ipynb')):
    """Accepts a pycharm console history and the outcome as input and outputs a report of the correct steps taken to
    achieve said outcome"""
    # console_log (string): name of a .txt file containing the console log
    # specified_outcome (string): the end result of the console session. The model will attempt to find all code
    #       necessary to achieve the outcome in the log.
    # outcome_line (integer): the number of the line where the outcome was produced.
    # output_name (string): the file name for the output file. (.ipynb)
    chat = model.start_chat(history=[])
    nb = nbf.v4.new_notebook()
    console_log = open(console_log).read()

    outcome_line = str(outcome_line)
    response = chat.send_message(
        'Eliminate all code from the console log which is not necessary to achieve the specified outcome as '
        'demonstrated in the specified line. Ensure all code is included that is necessary to run the specified line. '
        'Use only code from the console log.  Specified Outcome: ' + specified_outcome + '. Specified Line: ' + str(
            outcome_line) + '. Console Log: ' + console_log)
    response = chat.send_message(
        'Explain each section of the code you returned. Label the explanations and code chunks \' ~E~ <explanation '
        'text>. ~C~ <code>')

    nb['cells'].append(nbf.v4.new_markdown_cell('# Console Session Report (Automatically Generated)\n'
                                                '**Created by:** ' + os.environ.get('USERNAME') +
                                                '\n**Date:** ' + date.today().strftime("%B %d, %Y") +
                                                '\n**Model Version:** ' + model.model_name +
                                                '\n\n**Session outcome:** *' + specified_outcome + '*'))
    splits = chat.history[3].parts[0].text.split('~')
    for i in range(len(splits)):
        if i == 0:
            continue
        if (i == 1) | (i % 4 == 1):
            assert (splits[i] == 'E')
        elif (i == 2) | (i % 4 == 2):
            nb['cells'].append(nbf.v4.new_markdown_cell(splits[i]))
        elif (i == 3) | (i % 4 == 3):
            assert (splits[i] == 'C')
        elif i % 4 == 0:
            nb['cells'].append(nbf.v4.new_code_cell(re.search(r'(```python\n)([\d\D\n]*)(\n```)', splits[i])[2]))

    with open(output_name, 'w') as f:
        nbf.write(nb, f)
