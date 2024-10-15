from flask import Flask
from config import Config, Base
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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

from app import routes, models
