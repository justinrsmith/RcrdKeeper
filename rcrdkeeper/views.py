from rcrdkeeper import app
from flask import g, render_template, request, jsonify, session, redirect, abort
import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask.ext.mail import Message, Mail
import config
import emails
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from werkzeug import secure_filename
import os


from rdio import Rdio
rdio = Rdio(('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T'))
RCRDKEEPER_DB = 'rcrdkeeper'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

users = r.db('rcrdkeeper').table('users')
records = r.db('rcrdkeeper').table('records')


@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host='localhost', port=28015, db=RCRDKEEPER_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

    if 'user' in session:
        g.user = session['user']

        if request.endpoint == 'login':
            return redirect('/home')


@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close(noreply_wait=False)
    except AttributeError:
        pass


@app.route('/register', methods=['POST'])
def register():

    error = None

    if request.method == 'POST':

        user_exist = list(users.filter(
            {'email': request.form['email']}).run(g.rdb_conn))

        if user_exist:
            error = "Account with this email already exist. \
            Click 'forgot password' to recover your account."

            return render_template('login.html', error=error)
        else:
            hash_pw = generate_password_hash(
                request.form['register_password'])

            response = users.insert({
                          'name': request.form['name'],
                          'email': request.form['email'],
                          'password': hash_pw,
                          'birthdate': request.form['birthdate'],
                          'key': None}).run(g.rdb_conn)

            email_message = 'Thank you for registering with RcrdKeeper. No further action is required to use your account.'

            session['user'] = response['generated_keys'][0]

            succ = 'Account successfully created. You are now logged in. \
                You will recieve a confirmation email shortly.'

            if response['inserted'] == 1:
                emails.send_email('RcrdKeeper Registration Confirmation',
                    app.config['MAIL_USERNAME'],
                    request.form['email'], email_message)
         
        return render_template('home.html', succ=succ, first_login=True)


@app.route('/', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        cursor = users.filter(r.row['email'] == request.form['email']
                                                            ).run(g.rdb_conn)

        for c in cursor:
            email = c['email']
            password = c['password']
            session['user'] = c['id']
            session['user_full_name'] = c['name']

        if not 'email' in locals():
            email = None
            password = None
        else:
            valid_password = check_password_hash(
                password, request.form['password'])

        if request.form['email'] != email:
            error = 'Email address does not exist.'
        elif not valid_password:
            error = 'Invalid password.'
        else:
            session['logged_in'] = True
            
            return redirect('/home')
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():

    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')

@app.route('/home', methods=['GET'])
@app.route('/home/<int:page>', methods=['GET'])
def home(page=1):

    if not session.get('logged_in'):
        return render_template('login.html')
    artist = list(records.filter({
                        'user':g.user}).order_by(
                        'artist').pluck('artist').run(g.rdb_conn))

    artist = [dict(tupleized) for tupleized in set(
                        tuple(item.items()) for item in artist)]

    selection = list(records.filter(
        {'user':g.user}).order_by(
            'artist', 'album').skip((page-1)*16).limit(16).run(g.rdb_conn))

    rec_count = records.filter({'user': g.user}).count().run(g.rdb_conn)

    status_next = None
    if rec_count <= 16:
        status_next = 'disabled'

    status_prev = None
    if page == 1:
        status_prev = 'disabled'

    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    return render_template('home.html',
                            artist=artist,
                            selection=selection,
                            condition=condition,
                            size=size,
                            page=page,
                            status_next=status_next,
                            status_prev=status_prev,
                            user_name = session['user_full_name'])


@app.route('/get_records/<int:page>', methods=['GET'])
@app.route('/get_records/<int:page>/<string:artist>', methods=['GET'])
def get_records(page, artist=None):

    if artist == 'undefined':
        artist = None

    if not artist:
        selection = list(records.filter({'user': g.user}).order_by(
                        'artist', 'album').skip((page-1)*16).limit(
                            16).run(g.rdb_conn))
        rec_count = records.filter(
            {'user': g.user}).skip(
             (page-1)*16).count().run(g.rdb_conn)

    else:
        selection = list(records.filter({
                        'user': g.user, 'artist': artist}).order_by(
                        'artist', 'album').limit(16).run(g.rdb_conn))

    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    return render_template('records.html',
                            selection=selection,
                            condition=condition,
                            size=size)


@app.route('/list_records', methods=['GET'])
@app.route('/list_records/<string:artist>', methods=['GET'])
def list_records(artist=None):

    if artist == 'undefined':
        artist = None
        
    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    if not artist:
        selection = list(records.filter(
            {'user':g.user}).order_by(
                        'artist', 'album').run(g.rdb_conn))
    else:
        selection = list(records.filter(
            {'user':g.user, 'artist': artist}).order_by(
                        'artist', 'album').run(g.rdb_conn))

    return render_template('list_records.html',
                            selection=selection,
                            condition=condition,
                            size=size)


@app.route('/submit/<string:location>', methods=['POST', 'GET'])
def new_record(location):

    new_info = query(request.form, 'insert')

    condition = list(r.table('record_condition').order_by(
                                    'order').run(g.rdb_conn))

    size = list(r.table('record_size').order_by(
                                    'order').run(g.rdb_conn))

    record = records.get(new_info).run(g.rdb_conn)

    if location == 'grid':
        return render_template('new_record.html',
                                s=record,
                                condition=condition,
                                size=size)
    else:
        return render_template('add_list.html',
                                s=record,
                                condition=condition,
                                size=size)


@app.route('/edit', methods=['POST'])
def edit_record():

    new_info = query(request.form, 'edit')

    return redirect('/')


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id=None):

    a = records.get(record_id).run(g.rdb_conn)

    records.get(record_id).delete().run(g.rdb_conn)

    return a['artist'] + ' - ' + a['album']

@app.route('/get_albums/<string:artist>', methods=['GET'])
def get_albums(artist):

    artist_info = rdio.call('search', {'query': artist, 'types': 'artist'})

    artist_key = artist_info['result']['results'][0]['key']

    get_albums = rdio.call('getAlbumsForArtist', {'artist': artist_key})

    albums = []
    for i,x in enumerate(get_albums['result']):
        albums.append({'id':x['name'], 'text': x['name']})

    return jsonify(albums=albums)


@app.route('/forgot', methods=['POST'])
def forgot():

    if request.method == 'POST':

        email_exist = list(users.filter({
            'email': request.form['email']}).run(g.rdb_conn)).pop()

        if email_exist:
            key = hashlib.md5(email_exist['id']).hexdigest()
            
            users.get(email_exist['id']).update({'key': key}).run(g.rdb_conn)
        
            email_message = 'This email has receieved a request to reset password for RcrdKeeper. Follow the below link to reset rcrdkeeper.com/reset/' + key

            emails.send_email('RcrdKeeper Account Recovery',
                                app.config['MAIL_USERNAME'],
                                email_exist['email'],
                                email_message)

    return ''


@app.route('/reset', methods=['POST'])
@app.route('/reset/<string:key>', methods=['POST', 'GET'])
def reset(key=None):

    key_exists = users.filter({'key': key}).count().run(g.rdb_conn)

    if not key_exists == 0:
        user = list(users.filter({'key': key}).run(g.rdb_conn)).pop()

        if request.method == 'POST':

            hash_pw = generate_password_hash(request.form['verify_password'])
            users.get(user['id']).update({
                'password': hash_pw, 'key': None}).run(g.rdb_conn)
            session['logged_in'] = True
            session['user_full_name'] = str(users['name'])
            
            succ = 'Your password has been reset, you may now login.'
            return render_template('login.html',succ=succ)
    else:
        return redirect('/')

    return render_template('reset.html',
                            key=key)

@app.route('/contact', methods=['POST', 'GET'])
def contact():

    if request.method == 'POST':

        response = r.db('rcrdkeeper').table('contact').insert(
            [{'issue_type': request.form['issue_type'],
              'email': request.form['email'],
              'comment': request.form['comment']}]).run(g.rdb_conn)

        email_message = 'New request'

        if response['inserted'] == 1:
            emails.send_email('RcrdKeeper Registration Confirmation',
                                app.config['MAIL_USERNAME'],
                                request.form['email'],
                                email_message)

    return render_template('contact.html')


@app.route('/faq', methods=['GET'])
def faq():

    return render_template('faq.html')


def allowed_file(filename):

    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def query(form, query_type):

    album_info = rdio.call('search', {'query': form['album'],
                                         'types': 'album'})

    if album_info['result']['number_results'] != 0:
        for x in album_info['result']['results']:
            if x['artist'].upper() == form['artist'].upper():
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
                                'notes': '',
                                'user_artwork': ''}]).run(g.rdb_conn)

        selection = records.get(succ['generated_keys'][0]).run(g.rdb_conn)

        return succ['generated_keys'][0]
    elif query_type == 'edit':
        record = records.get(form['id']).run(g.rdb_conn)

        if request.files.get('artwork'):
            file = request.files['artwork']
            if file and allowed_file(file.filename):
                filename = secure_filename=(file.filename)
                file_location = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename).split('/',1 )[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif record['user_artwork']:
            file_location = record['user_artwork']
        else:
            file_location = ''

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
                            'size' : form['size'],
                            'user_artwork': file_location}).run(g.rdb_conn)

        return {'artist': form['artist'],
                        'album': form['album'],
                            'album art': album_art}


@app.route('/get_page/<int:page>')
def get_page(page):

    selection = list(records.filter({'user': g.user}).order_by(
                    'artist', 'album').skip((page-1)*16).limit(
                        16).run(g.rdb_conn))
    rec_count = records.filter(
        {'user': g.user}).skip(
         (page-1)*16).count().run(g.rdb_conn)

    status_next = None
    if rec_count <= 16:
        status_next = 'disabled'

    status_prev = None
    if page == 1:
        status_prev = 'disabled'

    return jsonify(status_prev=status_prev,
                   status_next=status_next)


     