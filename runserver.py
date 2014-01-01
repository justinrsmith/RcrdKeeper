import argparse
from flask import Flask, g, render_template, request, jsonify, flash, session, redirect, abort
import os
import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask.ext.mail import Message, Mail
import config
import emails
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


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

app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'flasktesting33@gmail.com',
    MAIL_PASSWORD = 'testpw2013'
)


mail = Mail(app)

users = r.db('rcrdkeeprapp').table('users')
records = r.db('rcrdkeeprapp').table('records')

@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host='localhost', port=28015, db=RCRDKEEPR_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

    if 'user' in session:
        g.user = session['user']

#@app.teardown_request
#def teardown_request(exception):
#    try:
#        g.rdb_conn.close()
#    except AttributeError:
#        pass

@app.route('/register', methods=['POST'])
def register():

    error = None

    if request.method == 'POST':

        user_exist = list(users.filter({'email': request.form['email']}).run(g.rdb_conn))

        if user_exist:
            error = "Account with this email already exist. \
            Click 'forgot password' to recover your account."
        else:
            hash_pw = generate_password_hash(request.form['register_password'])

            response = users.insert({'email': request.form['email'],
                          'password': hash_pw,
                          'birthdate': request.form['birthdate'],
                          'key': None}).run(g.rdb_conn)

            email_message = "Thank you for registering with RcrdKeepr."

            if response['inserted'] == 1:
                emails.send_email('RcrdKeepr Registration Confirmation','flasktesting33@gmail.com',
                                    request.form['email'], email_message)
         
        return render_template('login.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        cursor = users.filter(r.row['email'] == request.form['email']
                                                            ).run(g.rdb_conn)

        for c in cursor:

            email = c['email']
            password = c['password']
            session['user'] = c['id']

        

        if not 'email' in locals():
            email = None
            password = None
        else:
            valid_password = check_password_hash(password, request.form['password'])

        if request.form['email'] != email:
            error = 'Invalid email'
        elif not valid_password:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            
            flash('You were logged in')
            return redirect('/')
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():

    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect('/login')

@app.route('/', methods=['GET'])
def home():

    if not session.get('logged_in'):
        abort(401)

    artist = records.filter({
                        'user':g.user}).run(g.rdb_conn)

    selection = list(records.filter(
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

    selection = list(records.filter(
        {'artist':artist, 'user':g.user}).order_by('artist').run(g.rdb_conn))

    return render_template('records.html',
                            selection=selection)


@app.route('/submit', methods=['POST', 'GET'])
def new_record():

    new_info = query(request.form, 'insert')

    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    record = records.get(new_info).run(g.rdb_conn)

    return render_template('new_record.html',
                            s=record,
                            condition=condition,
                            size=size)


@app.route('/edit', methods=['POST'])
def edit_record():

    new_info = query(request.form, 'edit')

    print new_info

    return redirect('/')


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id=None):

    records.get(record_id).delete().run(g.rdb_conn)

    return ''

@app.route('/get_albums', methods=['GET'])
def get_albums():

    print request.form

    test = ['a', 'b']

    return jsonify(test2=test)


@app.route('/forgot', methods=['POST'])
def forgot():

    if request.method == 'POST':

        email_exist = list(users.filter({
            'email': request.form['email']}).run(g.rdb_conn)).pop()

        if email_exist:
            key = hashlib.md5(email_exist['id']).hexdigest()
            
            users.get(email_exist['id']).update({'key': key}).run(g.rdb_conn)
        
            email_message = 'Follow the below link to reset 10.0.0.8:4000/reset/' + key

            emails.send_email('RcrdKeepr Account Recovery','flasktesting33@gmail.com',
                                email_exist['email'], email_message)

    return ''

@app.route('/reset', methods=['POST'])
@app.route('/reset/<string:key>', methods=['POST', 'GET'])
def reset(key=None):

    print 'hihihi'
    if key:
        user = list(users.filter({'key': key}).run(g.rdb_conn)).pop()
        session['user'] = user['id']

    print request.method
    if request.method == 'POST':
        hash_pw = generate_password_hash(request.form['verify_password'])
        users.get(session['user']).update({
            'password': hash_pw, 'key': None}).run(g.rdb_conn)
        session['logged_in'] = True

        return redirect('/')

    return render_template('reset.html')



def query(form, query_type):

    album_info = rdio.call('search', {'query': form['album'],
                                         'types': 'album'})

    if album_info['result']['number_results'] != 0:
        for x in album_info['result']['results']:

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

        print succ['generated_keys'][0]

        selection = records.get(succ['generated_keys'][0]).run(g.rdb_conn)
        #print selection
        #return selection
        return succ['generated_keys'][0]
    elif query_type == 'edit':
        records.get(form['id']).update({
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
        app.run(host='localhost', port=4000, debug=True)
