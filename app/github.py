# Responsible for communicating w GitHub API formatting data
import os
from dotenv import load_dotenv
import requests
from requests import HTTPError
from github import Github, Auth

from app import app, db
from datetime import datetime
from pprint import pprint
import json

load_dotenv()

GH_API_URL = "https://api.github.com"

class GetGitHub:
    def __init__(self, user):
        self._user = user
        self._token = os.environ["GITHUB_TOKEN"]
        self.events = self.get_events(user=self._user, token=self._token)
        self.commits = self.commit_activity(user=self._user, token=self._token)
        self.repo_activity = self.recent_repo_activity(user=self._user, token=self._token)

    def get_events(self, user, token):
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {
                "per_page": 100
            }

        user_events = f"{GH_API_URL}/users/{user}/events"

        response = requests.get(url=user_events, headers=headers, params=payload)
        response.raise_for_status()
        # print(f"url: {response.url}")
        # print(f"headers: {response.headers}")
        # print(f"my headers: {response.request.headers}")

        events = response.json()

        all_events = []

        for i in events:
            event_id = i["id"]
            event_type = i["type"]
            repo = i["repo"]["name"].split("/")[1]
            repo_id = i["repo"]["id"]
            event_timestamp = i["created_at"].strip("Z")

            if i['type'] == "PushEvent":
                commits = int(i["payload"]["size"])
                event = {
                    "timestamp": datetime.fromisoformat(event_timestamp),
                    "action": f"Pushed {commits} commit(s) to ",
                    "repo": repo
                }

            elif i["type"] == "CreateEvent":
                create_type = i["payload"]["ref_type"]
                event = {
                    "timestamp": datetime.fromisoformat(event_timestamp),
                    "action": f"Created {create_type} in ",
                    "repo": repo
                }

            all_events.append(event)

        # print(f"all_events: {len(all_events)}")
        return all_events

    def recent_repos(self):
        recent = []
        for i in self.events:
            if i["repo"] not in recent:
                recent.append(i["repo"])
        # print(f"recent repos: {recent}")
        # print(f"len: {len(recent)}")
        return recent

    def commit_activity(self, user, token):
        repo_list = self.recent_repos()
        weekly_commits = []
        # print(len(repo_list))

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # make sure list is not empty
        if len(repo_list) > 0:
            for repo in repo_list:
                # Endpoint to get weekly commit count as list, with index 0 being 52 weeks ago
                # Problem with this is only counts commits on default branches
                weekly_count = f"{GH_API_URL}/repos/{user}/{repo}/stats/participation"

                response = requests.get(url=weekly_count, headers=headers)
                response.raise_for_status()
                data = response.json()

                add_activity = {
                    repo: data
                }

                weekly_commits.append(add_activity)
        # print(f"weekly commits: {weekly_commits}")
        # Sample output with weekly commits numbers
        # weekly commits: [{'my-learning': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 42, 10, 29, 32, 34, 19, 6, 7, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 42, 10, 29, 32, 34, 19, 6, 7, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 0, 0]}}, {'my-rise': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4]}}, {'dashboard': {'all': [], 'owner': []}}, {'interactive-charting-flask': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0]}}, {'avocado-analytics-dash': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0]}}, {'health-data': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0]}}]
        return weekly_commits
    # def recent_repo_activity(self, user, token):
    #     repo_list = self.recent_repos()
    #     repo_activity = []
    #
    #     headers = {
    #         "accept": "application/vnd.github+json",
    #         "authorization": f"Bearer {token}",
    #         "X-GitHub-Api-Version": "2022-11-28"
    #     }
    #     # Limit activity to 3 months
    #     params = {
    #         "time_period": "quarter"
    #     }
    #
    #     # make sure list is not empty
    #     if len(repo_list) > 0:
    #         for repo in repo_list:
    #             # Endpoint to get detailed repo activity
    #             activity_url = f"{GH_API_URL}/repos/{user}/{repo}/activity"
    #
    #             response = requests.get(url=activity_url, headers=headers, params=params)
    #             response.raise_for_status()
    #             data = response.json()
    #
    #             add_activity = {
    #                 repo: data
    #             }
    #
    #             repo_activity.append(add_activity)
    #         # dump output to file for testing
    #         with open("recent-repo-activity.json", "a") as file:
    #             json.dump(repo_activity, file)

    def recent_repo_activity(self, user, token):
        repo_list = self.recent_repos()
        all_repo_events = []

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        params = {
            "per_page": 100
        }

        # make sure list is not empty
        if len(repo_list) > 0:
            for repo in repo_list:
                # Endpoint to get repo events
                events_url = f"{GH_API_URL}/repos/{user}/{repo}/events"

                response = requests.get(url=events_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                repo_events = {
                    "repo": repo,
                    "timestamp": [],
                    "values": []
                }

                # parse events data per repo
                for event in data:
                    event_type = event["type"]
                    created = event["created_at"].strip("Z")
                    date = created.split("T")[0]

                    if event_type == "PushEvent":
                        repo_events["timestamp"].append(date)
                        # repo_events["type"].append(event_type)
                        commits = int(event["payload"]["size"])
                        repo_events["values"].append(commits)

                    # elif event_type == "CreateEvent":
                        # create_type = event["payload"]["ref_type"]
                        # repo_events["payload_target"].append(create_type)

                all_repo_events.append(repo_events)

            # print(f"all repo events: {all_repo_events}")
            return all_repo_events
            # # dump output to file for testing
            # with open("recent-repo-events.json", "a") as file:
            #     json.dump(repo_events, file)
