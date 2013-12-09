import argparse
from flask import Flask, g, render_template, request, jsonify, flash, session, redirect, abort
import os
import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

from rdio import Rdio
rdio = Rdio(('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T'))
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

    g.user = '7f0415cb-49d7-421b-9eeb-8f9a0fbb94f6'

#@app.teardown_request
#def teardown_request(exception):
#    try:
#        g.rdb_conn.close()
#    except AttributeError:
#        pass

@app.route('/register', methods=['POST'])
def register():

    users = r.db('rcrdkeeprapp').table('users')

    users.insert({'username': request.form['username'],
                  'password': request.form['password']}).run(g.rdb_conn)

    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():

    users = r.db('rcrdkeeprapp').table('users')
    error = None

    if request.method == 'POST':
        cursor = users.filter(r.row['username'] == request.form['username']
                                                            ).run(g.rdb_conn)
        for c in cursor:

            username = c['username']
            password = c['password']
            session['user'] = c['id']

        if not 'username' in locals():
            username = None
            password = None

        if request.form['username'] != username:
            error = 'Invalid username'
        elif request.form['password'] != password:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            
            flash('You were logged in')
            return redirect('/')
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():

    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('/login')

@app.route('/', methods=['GET'])
def home():

    if not session.get('logged_in'):
        abort(401)

    print g.user

    artist = list(r.table('records').pluck('artist').filter({
                        'user':g.user}).distinct().run(g.rdb_conn))

    selection = list(r.table('records').filter(
        {'user':g.user}).order_by('artist').run(g.rdb_conn))

    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    return render_template('home.html',
                            artist=artist,
                            selection=selection,
                            condition=condition,
                            size=size)

@app.route('/get_records/<string:artist>', methods=['GET'])
def get_records(artist):

    selection = list(r.table('records').filter(
        {'artist':artist, 'user':g.user}).order_by('artist').run(g.rdb_conn))

    return render_template('records.html',
                            selection=selection)

@app.route('/submit', methods=['POST', 'GET'])
def new_record():

    new_info = query(request.form, 'insert')

    return render_template('new_record.html',
                            new_info=new_info)


@app.route('/edit', methods=['POST'])
def edit_record():

    new_info = query(request.form, 'edit')

    return new_info['album art']


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id=None):

    records = r.db('rcrdkeeprapp').table('records')

    records.get(record_id).delete().run(g.rdb_conn)

    return ''

@app.route('/get_albums', methods=['GET'])
def get_albums():

    test = ['a', 'b']

    return jsonify(test2=test)

def query(form, query_type):

    records = r.db('rcrdkeeprapp').table('records')

    album_info = rdio.call('search', {'query': form['album'],
                                         'types': 'album'})

    if album_info['result']['number_results'] != 0:
        for x in album_info['result']['results']:
            print 'for'
            if x['artist'] == form['artist']:
                album_art = x['icon']
                release_date = x['releaseDate']
                duration = x['duration']
                duration = duration/60
                tracks = x['length']
                artist_key = x['artistKey']
                break
            else:
                album_art = 'http://musicunderfire.com/wp-content/uploads/2012/06/No-album-art-itunes-300x300.jpg'
                release_date = ''
                duration = 0
                tracks = 0
                artist_key = ''
    else:
        album_art = 'http://musicunderfire.com/wp-content/uploads/2012/06/No-album-art-itunes-300x300.jpg'
        release_date = ''
        duration = 0
        tracks = 0
        artist_key = ''

    if query_type == 'insert':
        print 'insert'
        succ = records.insert([{'user': g.user,
                                'artist': form['artist'],
                                'album': form['album'],
                                'album art': album_art,
                                'release_date': release_date,
                                'duration': duration,
                                'tracks': tracks,
                                'record_condition': '',
                                'sleeve_condition': '',
                                'color': '',
                                'size': '',
                                'notes': ''}]).run(g.rdb_conn)

        return [{'artist': form['artist'],
                        'album': form['album'],
                            'album art': album_art}]
    elif query_type == 'edit':
        print 'edit'
        records.get(request.form['id']).update({
                                        'user': g.user,
                                        'artist': form['artist'],
                                        'album': form['album'],
                                        'album art': album_art,
                                        'release_date': release_date,
                                        'duration': duration,
                                        'tracks': tracks,
                                        'record_condition': form['record_condition'],
                                        'sleeve_condition': form['sleeve_condition'],
                                        'color': form['color'],
                                        'notes': form['notes'],
                                        'size' : form['size']}).run(g.rdb_conn)
        return {'artist': form['artist'],
                        'album': form['album'],
                            'album art': album_art}
    else:
        print 'failure'

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        app.run(host='localhost', debug=True)