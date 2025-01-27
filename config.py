from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DB_URI"]

    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_PORT = int(os.environ["MAIL_PORT"])
    MAIL_USE_TLS = os.environ["MAIL_USE_TLS"] is not None
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    ADMINS = ['testemail.ksg.data@gmail.com']


class Base(DeclarativeBase):
    pass
