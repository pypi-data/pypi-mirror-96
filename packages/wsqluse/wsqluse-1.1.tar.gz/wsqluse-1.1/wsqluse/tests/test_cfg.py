from wsqluse.wsqluse import Wsqluse


# База данных для тестов
db_name = 'wdb'
db_user = 'watchman'
db_pass = 'hect0r1337'
db_host = '192.168.100.109'

# Данные для тестов
kvt = {'table': {'name': 'auto'},
       'first': {'key': 'car_number', 'value': 'Х111ХХ111'},
       'second': {'key': 'id_type', 'value': 'tails'}}


wsqlshell = Wsqluse(db_name, db_user, db_pass, db_host, debug=True)
