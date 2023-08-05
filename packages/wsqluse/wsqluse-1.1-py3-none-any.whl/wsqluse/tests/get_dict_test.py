from wsqluse.tests.test_cfg import *
from wsqluse.tests.general_test_funcs import *

def analyse_correct_response(response):
    print('analysing')
    if type(response) == list():
        print('Test success')
    else:
        print('Test failed')


def test_correct_return():
    command = "SELECT * from {}".format(kvt['table']['name'])
    response = wsqlshell.get_table_dict(command)
    print('\n\n\n\n\n', response)
    analyze_response(response)


test_correct_return()
