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
        self.user = user
        self.user_id = user_id
        self.etag = self.get_user_etag()

    def get_user_etag(self):
        print(f"Getting user etag....")
        # user = db.session.execute(db.select(User).where(User.id) == self.user_id).scalar()
        user = db.get_or_404(User, self.user_id)
        print(f"Got user: {user}")
        if user:
            last_repos_call = user.last_called_repos
            etag = user.latest_etag_repos
            print(f"user etag: {etag}")

        if etag:
            print(f"get_etag_returned: {etag}")
            self.etag = etag
            return etag

    def set_user_etag(self, etag, timestamp):
        print(f"Setting user etag...")
        # user = db.session.execute(db.select(User).where(User.id) == self.user_id).scalar()
        user = db.get_or_404(User, self.user_id)
        print(f"Got user: {user}")
        if user:
            print(f"new timestamp: {timestamp}")
            print(f"new-etag: {etag}")
            user.last_called_repos = timestamp
            user.latest_etag_repos = etag

            print("Successfully changed etag data:")
            # print(f"new timestamp: {timestamp}")
            # print(f"new-etag: {etag}")

            db.session.commit()




