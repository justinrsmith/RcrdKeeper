from rcrdkeeper import app

app.secret_key = 'fsadfsdafsafsdgrberbebebe'
app.config['SERVER_NAME'] = 'rcrdkeeper.com'
app.config['UPLOAD_FOLDER'] = '/var/www/RcrdKeeper/rcrdkeeper/static/user_albums/'
app.config.from_object(__name__)

app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = '**',
    MAIL_PASSWORD = '**'
)