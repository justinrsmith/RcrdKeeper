import argparse
from flask import Flask, g, render_template, request, jsonify, flash
import os
import json
import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError, RqlDriverError

from rdio import Rdio
rdio = Rdio(('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T'))
#RDB_HOST =  os.environ.get('localhost')
#RDB_PORT = os.environ.get(28015) 
RCRDKEEPR_DB = 'rcrdkeeprapp'


def dbSetup():
    connection = r.connect(host='localhost', port=28015)
    try:
        r.db_create(RCRDKEEPR_DB).run(connection)
        r.db(RCRDKEEPR_DB).table_create('records').run(connection)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        connection.close()


app = Flask(__name__)
app.secret_key = 'some_secret'
app.config.from_object(__name__)


@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host='localhost', port=28015, db=RCRDKEEPR_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

#@app.teardown_request
#def teardown_request(exception):
#    try:
#        g.rdb_conn.close()
#    except AttributeError:
#        pass


@app.route('/records', methods=['GET'])
def get_records():
    selection = list(r.table('records').run(g.rdb_conn))

    return render_template('records.html',
                            selection=selection)

@app.route('/submit', methods=['POST', 'GET'])
def new_record():

    records = r.db('rcrdkeeprapp').table('records')

    #query for album info
    album_info = rdio.call('search', {'query': request.form['album'], 'types':
                                             'album'})

    #retrieve album artwork
    for x in album_info['result']['results']:
        if x['artist'] == request.form['artist']:
            album_art = x['icon']
            release_date = x['releaseDate']
            duration = x['duration']
            duration = duration/60

    new_info = [{'artist': request.form['artist'],
                        'album': request.form['album'],
                            'album art': album_art}]

    #insert album info
    succ = records.insert([{'artist': request.form['artist'],
                        'album': request.form['album'],
                            'album art': album_art,
                            'release_date': release_date,
                            'duration': duration}]).run(g.rdb_conn)

    return render_template('new_record.html',
                            new_info=new_info)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        app.run(host='10.0.0.15', debug=True)