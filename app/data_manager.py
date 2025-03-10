# Responsible for communicating w db, getting/formatting any data github API will need, return
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, date, timedelta
import json

from app import db
from app.models import User, Repository


load_dotenv()

GH_API_URL = "https://api.github.com"

class DataManager:
    """
    table: users
    last_called_repos: timestamp w last outgoing API call <datetime>
    latest_etag_repos: E-Tag from latest call response headers <str>
    """
    def __init__(self, user, user_id):
        self._user = user
        self._user_id = user_id

    def get_user_etag(self):
        user = db.session.execute(db.select(User).where(User.id) == self._user_id).scalar()
        if user:
            last_repos_call = user.last_called_repos
            etag = user.latest_etag_repos

