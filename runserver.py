from rcrdkeeper import app
import argparse
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


RCRDKEEPER_DB = 'rcrdkeeper'

def dbSetup():
    connection = r.connect(host='localhost', port=28015)
    try:
        r.db_create(RCRDKEEPER_DB).run(connection)
        r.db(RCRDKEEPER_DB).table_create('records').run(connection)
        r.db(RCRDKEEPER_DB).table_create('users').run(connection)
        r.db(RCRDKEEPER_DB).table_create('record_condition').run(connection)
        r.db(RCRDKEEPER_DB).table_create('record_size').run(connection)
        r.db(RCRDKEEPER_DB).table_create('contact').run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'M','condition':'Mint', 'order': 1}).run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'VG','condition':'Very Good', 'order': 2}).run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'G','condition':'Good', 'order': 3}).run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'AV','condition':'Average', 'order': 4}).run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'P','condition':'Poor', 'order': 5}).run(connection)
        r.db('rcrdkeeper').table('record_condition').insert({'abbr':'VP','condition':'Very Poor', 'order': 6}).run(connection)
        r.db('rcrdkeeper').table('record_size').insert({'size':'12 inch', 'order': 1}).run(connection)
        r.db('rcrdkeeper').table('record_size').insert({'size':'10 inch', 'order': 2}).run(connection)
        r.db('rcrdkeeper').table('record_size').insert({'size':'7 inch', 'order': 3}).run(connection)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        app.run(host='10.0.0.8', port=4000, debug=True)
