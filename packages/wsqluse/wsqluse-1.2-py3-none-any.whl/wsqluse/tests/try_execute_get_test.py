from wsqluse.tests.test_cfg import *

command = "SELECT * from {}".format(kvt['table']['name'])
response = wsqlshell.try_execute_get(command)
print('response:', response)