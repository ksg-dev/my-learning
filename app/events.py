# Responsible for communicating w GitHub API, formatting events data
import os
from dotenv import load_dotenv
import requests
from app import app, db
from app.models import Event
from datetime import datetime
from pprint import pprint

load_dotenv()

GH_TOKEN = os.environ["GITHUB_TOKEN"]
GH_USERNAME = os.environ["GITHUB_USERNAME"]

GH_API_URL = "https://api.github.com/"

class GetEvents:
    def __init__(self, user):
        self.user = user
        self.token = GH_TOKEN
        self.events = self.get_events(user)

    def get_events(self, user):
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        user_events = f"{GH_API_URL}users/{user}/events"

        response = requests.get(url=user_events, headers=headers)
        response.raise_for_status()
        events = response.json()

        all_events = []

        for i in events:
            if i['type'] == "PushEvent":
                new_event = {
                    "id": i["id"],
                    "type": "push",
                    "repo": i["repo"]["name"].split("/")[1],
                    "repo_id": i["repo"]["id"],
                    "commits": i["payload"]["size"],
                    "create_type": None,
                    "timestamp": i["created_at"].strip("Z")
                }

            elif i["type"] == "CreateEvent":
                new_event = {
                    "id": i["id"],
                    "type": "create",
                    "repo": i["repo"]["name"].split("/")[1],
                    "repo_id": i["repo"]["id"],
                    "commits": None,
                    "create_type": i["payload"]["ref_type"],
                    "timestamp": i["created_at"].strip("Z")
                }

            all_events.append(new_event)

        return all_events


def validate_id(model, ref_id):
    check = db.session.execute(db.select(model).filter_by(id=ref_id)).first()
    return check

