from flask import Flask
from config import Config, Base
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config.from_object(Config)
app.app_context().push()

db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)

# db migration engine object
migrate = Migrate(app, db, render_as_batch=True)

from app import routes, models
