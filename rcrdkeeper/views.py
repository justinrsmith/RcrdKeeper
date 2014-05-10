from rcrdkeeper import app
from flask import g, render_template, request, jsonify, session,\
                  redirect, abort
import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask.ext.mail import Message, Mail
import config
import emails
import hashlib
from werkzeug import secure_filename
import os
from rdio import Rdio
import datetime
from pytz import timezone
from rcrdkeeper import models as m
from werkzeug.security import generate_password_hash

rdio = Rdio(('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T'))
RCRDKEEPER_DB = 'rcrdkeeper'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG', 'PNG', 'JPEG'])

users = r.db('rcrdkeeper').table('users')
records = r.db('rcrdkeeper').table('records')


@app.before_request
def before_request():

    try:
        g.rdb_conn = r.connect(host='localhost', port=28015, db=RCRDKEEPER_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

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
        user_exist = m.User.get(email=request.form['email'])

        if user_exist:
            error = "Account with this email already exist. \
            Click 'forgot password' to recover your account."

            return render_template('login.html', error=error)
        else:
            hash_pw = generate_password_hash(
                request.form['register_password'])

            new_user = m.User()

            new_user.name      = request.form['name']
            new_user.email     = request.form['email']
            new_user.password  = hash_pw
            new_user.birthdate = request.form['birthdate']
            new_user.key       = None

            new_user.save()

            email_message = 'Thank you for registering with RcrdKeeper. No further action is required to use your account.'

            session['user'] = new_user['id']

            succ = 'Account successfully created. You are now logged in. \
                You will recieve a confirmation email shortly.'

            emails.send_email('RcrdKeeper Registration Confirmation',
                app.config['MAIL_USERNAME'],
                request.form['email'], email_message)

        return render_template('home.html', succ=succ, first_login=True)


@app.route('/', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        auth_user = m.User.auth_user(request.form['email'],
                                request.form['password'])

        if auth_user['status']:
            user = m.User.get(email=request.form['email'])

            session['logged_in'] = True
            session['email'] = user['email']
            session['user'] = user['id']
            session['user_full_name'] = user['name']

            return redirect('/home')
        else:
            if not auth_user['is_user']:
                error = 'Email address %s does not exist.' % request.form['email']
                session['logged_in'] = False
                session.clear()
            elif not auth_user['valid_password']:
                error = 'Invalid password.'
                session['logged_in'] = False
                session.clear()

    return render_template('login.html',  error=error)


@app.route('/logout')
def logout():

    session.clear()
    return redirect('/')

@app.route('/home', methods=['GET'])
def home():

    if not session.get('logged_in'):
        return render_template('login.html')

    get_artist = m.Records.filter(
        user=session['user']).order_by('artist').fetch()

    artist_list = []
    for a in get_artist:
        artist_list.append(a['artist'])

    artist_list = list(set(artist_list))
    artist_list.sort()

    selection = m.Records.filter(
        user=session['user']).order_by(
        'artist', 'album').limit(16).fetch()

    rec_count = len(m.Records.filter(user=session['user']).fetch())

    condition = m.Condition.order_by('order').fetch()

    size = m.Size.order_by('order').fetch()

    return render_template('home.html',
                            artist_list=artist_list,
                            selection=selection,
                            condition=condition,
                            size=size,
                            user_name = session['user_full_name'])


@app.route('/get_records/<int:page>', methods=['GET'])
@app.route('/get_records/<int:page>/<string:artist>', methods=['GET'])
@app.route('/list_records/<int:page>/', methods=['GET'])
@app.route('/list_records/<string:artist>', methods=['GET'])
@app.route('/get_records/<int:page>/<string:sort>', methods=['GET'])
def get_records(page, artist=None, sort=None):

    if artist == 'undefined':
        artist = None

    if not artist and not sort:
        selection = m.Records.filter(
            user=session['user']).order_by(
            'artist', 'album').offset((page-1)*16).limit(16).fetch()
    elif sort:

        selection = m.Records.filter(
            user=session['user']).order_by(
            'date_added').fetch()
        selection.reverse()
        selection = selection[((page-1)*16):((page-1)*16)+16]

    else:
        selection = m.Records.filter(
            user=session['user'], artist=artist).order_by(
            'artist', 'album').offset((page-1)*16).limit(16).fetch()

    condition = m.Condition.order_by('order').fetch()

    size = m.Size.order_by('order').fetch()

    record_count = len(selection)
    record_count_total = len(m.Records.filter(user=session['user']).fetch())
    last_page = record_count_total-(16*page)

    if not 'list_records' in request.path:
        return render_template('records.html',
                                selection=selection,
                                condition=condition,
                                size=size,
                                record_count=record_count,
                                last_page=last_page)
    else:
        return render_template('list_records.html',
                        selection=selection,
                        condition=condition,
                        size=size,
                        record_count=record_count,
                        last_page=last_page)


@app.route('/submit/<string:location>', methods=['POST', 'GET'])
def new_record(location):

    album_info = rdio.call('search', {'query': request.form['album'],
                                         'types': 'album'})

    if album_info['result']['number_results'] != 0:
        for x in album_info['result']['results']:
            if x['artist'].upper() == request.form['artist'].upper():
                album_art    = x['icon']
                release_date = x['releaseDate']
                duration     = x['duration']
                duration     = duration/60
                tracks       = x['length']
                artist_key   = x['artistKey']
    else:
        album_art = 'http://musicunderfire.com/wp-content/uploads/2012/06/No-album-art-itunes-300x300.jpg'
        release_date = ''
        duration = 0
        tracks = 0
        artist_key = ''

    new_record = m.Records()

    new_record.user     = session['user']
    new_record.artist   = request.form['artist']
    new_record.album    = request.form['album']
    new_record.album_art = album_art
    new_record.release_date = release_date
    new_record.duration     = duration
    new_record.tracks   = tracks
    new_record.record_condition = ''
    new_record.sleeve_condition = ''
    new_record.color = ''
    new_record.size  = ''
    new_record.notes = ''
    new_record.date_added = r.expr(datetime.datetime.now(
                        timezone('US/Central')))
    new_record.user_artwork=''

    new_record.save()

    condition = m.Condition.order_by('order').fetch()

    size = m.Size.order_by('order').fetch()

    record = m.Records.get(id=new_record['id'])

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

    record = m.Records.get(id=request.form['id'])

    if request.files.get('artwork'):
        file = request.files['artwork']
        if file and allowed_file(file.filename):
            filename = secure_filename=(file.filename)
            file_location = 'http://rcrdkeeper.com/static/user_albums/' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    elif record['user_artwork']:
        file_location = record['user_artwork']
    else:
        file_location = ''

    record.format = request.form['format']
    record.color = request.form['color']
    record.notes = request.form['notes']
    record.size  = request.form['size']
    record.artist       = request.form['artist']
    record.album        = request.form['album']
    record.user_artwork     = file_location
    record.record_condition = request.form['record_condition']
    record.sleeve_condition = request.form['sleeve_condition']

    record.save()

    return redirect('/')


@app.route('/wish_list/', methods=['POST', 'GET'])
def wish_list():

    if request.method == 'POST':
        print request.form['artist']
        print request.form['album']


    return render_template('wish_list.html')


@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id=None):

    record = m.Records(record_id)
    record.delete()

    return record['artist'] + ' - ' + record['album']

@app.route('/get_albums/<string:artist>', methods=['GET'])
def get_albums(artist):

    artist_info = rdio.call('search', {'query': artist, 'types': 'artist'})

    if not artist_info['result']['number_results'] == 0:
        artist_key = artist_info['result']['results'][0]['key']

        get_albums = rdio.call('getAlbumsForArtist', {'artist': artist_key})

        albums = []
        for i,x in enumerate(get_albums['result']):
            albums.append({'id':x['name'], 'text': x['name']})
    else:
        albums = ''

    return jsonify(albums=albums)


@app.route('/forgot', methods=['POST'])
def forgot():

    if request.method == 'POST':

        email_exist = m.User.get(email=request.form['email'])

        if email_exist:
            key = hashlib.md5(email_exist['id']).hexdigest()

            user = m.User.get(id=email_exist['id'])
            user.key = key
            user.save()

            email_message = 'This email has receieved a request to reset password for RcrdKeeper. Follow the below link to reset rcrdkeeper.com/reset/' + key

            emails.send_email('RcrdKeeper Account Recovery',
                                app.config['MAIL_USERNAME'],
                                email_exist['email'],
                                email_message)

    return None


@app.route('/reset', methods=['POST'])
@app.route('/reset/<string:key>', methods=['POST', 'GET'])
def reset(key=None):

    user_has_key = m.User.get(key=key)

    if user_has_key:
        if request.method == 'POST':

            hash_pw = generate_password_hash(request.form['verify_password'])

            user_has_key.password = hash_pw
            user_has_key.key = None
            user_has_key.save()

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

        contact = m.Contact(
                issue_type=request.form['issue_type'],
                email=request.form['email'],
                comment=request.form['comment']
            )

        email_message = contact['comment']

        emails.send_email('RcrdKeeper Registration Confirmation',
                            app.config['MAIL_USERNAME'],
                            app.config['MAIL_USERNAME'],
                            email_message)

    return render_template('contact.html')


@app.route('/faq', methods=['GET'])
def faq():

    return render_template('faq.html')


def allowed_file(filename):

    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS