import argparse
from flask import Flask, g, render_template, request, jsonify, flash
import os
import json
import rethinkdb as r
#import urllib2
#import simplejson

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
    selection = list(r.table('records').order_by(
                                    'artist').run(g.rdb_conn))

    #req = urllib2.Request("https://itunes.apple.com/lookup?upc=720642462928")
    #opener = urllib2.build_opener()
    #f = opener.open(req)
    #print f.read()

    condition = list(r.table('record_condition').run(g.rdb_conn))

    size = list(r.table('record_size').run(g.rdb_conn))

    return render_template('records.html',
                            selection=selection,
                            condition=condition,
                            size=size)

@app.route('/submit', methods=['POST', 'GET'])
def new_record():

    records = r.db('rcrdkeeprapp').table('records')

    #query for album info
    album_info = rdio.call('search', {'query': request.form['album'],
                                         'types': 'album'})

    #retrieve album artwork
    for x in album_info['result']['results']:
        if x['artist'] == request.form['artist']:
            album_art = x['icon']
            release_date = x['releaseDate']
            duration = x['duration']
            duration = duration/60
            tracks = x['length']
            artist_key = x['artistKey']

#    album_info_extend = rdio.call('getAlbumsForArtist', 
#                                {'query': artist_key, 'artist': artist_key})

    new_info = [{'artist': request.form['artist'],
                        'album': request.form['album'],
                            'album art': album_art}]

    #insert album info
    succ = records.insert([{'artist': request.form['artist'],
                        'album': request.form['album'],
                            'album art': album_art,
                            'release_date': release_date,
                            'duration': duration,
                            'tracks': tracks,
                            'record_condition': '',
                            'sleeve_condition': '',
                            'color': '',
                            'size': '',
                            'notes': ''}]).run(g.rdb_conn)

    return render_template('new_record.html',
                            new_info=new_info)


@app.route('/edit', methods=['POST'])
def edit_record():

    print request.form
    records = r.db('rcrdkeeprapp').table('records')

    records.get(request.form['id']).update({
                    'record_condition': request.form['record_condition'],
                    'sleeve_condition': request.form['sleeve_condition'],
                    'color': request.form['color'],
                    'notes': request.form['notes'],
                    'size' : request.form['size']}).run(g.rdb_conn)

    return ''


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id=None):

    records = r.db('rcrdkeeprapp').table('records')

    records.get(record_id).delete().run(g.rdb_conn)

    return ''

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        app.run(host='localhost', debug=True)