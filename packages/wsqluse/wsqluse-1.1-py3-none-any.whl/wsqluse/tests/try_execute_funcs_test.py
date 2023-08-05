# Тесты для wsqluse

from wsqluse.tests.test_cfg import *
from wsqluse.tests.general_test_funcs import *


def try_execute_test():
    # INSERT OPERATION
    command = "INSERT INTO {} ({}, {})  values ('{}', '{}')".format(kvt['table']['name'],
                                                                    kvt['first']['key'], kvt['second']['key'],
                                                                    kvt['first']['value'], kvt['second']['value'])
    response = wsqlshell.try_execute(command)
    analyze_response(response)

def delete_operation():
    # DELETE OPERATION
    command = "DELETE FROM {} where {}='{}' and {}='{}'".format(kvt['table']['name'],
                                                                    kvt['first']['key'], kvt['first']['value'],
                                                                    kvt['second']['key'], kvt['second']['value'])
    response = wsqlshell.try_execute(command)
    analyze_response(response)


if __name__ == '__main__':
    try_execute_test()
    delete_operation()
