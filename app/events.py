# Responsible for communicating w GitHub API, formatting events data
import os
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()

GH_TOKEN = os.environ["GITHUB_TOKEN"]
GH_USERNAME = os.environ["GITHUB_USERNAME"]

GH_API_URL = "https://api.github.com/"

class GetEvents:
    def __init__(self):
        self.user = GH_USERNAME
        self.token = GH_TOKEN
        self.events = self.get_events(GH_USERNAME)

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

        return events

