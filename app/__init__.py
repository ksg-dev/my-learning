from flask import Flask
from config import Config, Base
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(Config)
app.app_context().push()

db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)