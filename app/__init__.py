from flask import Flask
from config import Config, Base
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)

app.config.from_object(Config)
app.app_context().push()

db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# db migration engine object
migrate = Migrate(app, db, render_as_batch=True)


# Log errors by email
# If app debug false
if not app.debug:
    # if mail server in config
    if app.config['MAIL_SERVER']:
        # Establish auth variable and set to None
        auth = None
        # If email username or password in config
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            # auth tuple updated with username and password
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        # Est secure variable and set to None
        secure = None
        # If mail use tls is not none, set secure to empty tuple for tls secure protocol
        if app.config['MAIL_USE_TLS']:
            secure = ()
        # create SMTPHandler object
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='My-Learning Failure',
            credentials=auth, secure=secure
        )
        # Set level to report errors and not warnings
        mail_handler.setLevel(logging.ERROR)
        # Attach handler to app.logger object from Flask
        app.logger.addHandler(mail_handler)


from app import routes, models, errors
