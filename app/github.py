# Responsible for communicating w GitHub API formatting data
import os
from dotenv import load_dotenv
import requests
from requests import HTTPError
from github import Github, Auth

from app import app, db
from datetime import datetime, date, timedelta
from pprint import pprint
import json


load_dotenv()

GH_API_URL = "https://api.github.com"

class GetGitHub:
    def __init__(self, user):
        self._user = user
        self._token = os.environ["GITHUB_TOKEN"]
        self.events = self.get_events(user=self._user, token=self._token)
        self.recent_repos = self.get_recent_repos(token=self._token)
        # self.commits = self.commit_activity(user=self._user, token=self._token, repo_list=self.recent_repos["repo"])
        self.repo_activity = self.recent_repo_activity(user=self._user, token=self._token)
        # self.py_data = self.pygithub_get_commits(token = self._token, user=self._user)

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

    def get_recent_repos(self, token):

        # Get today's date
        today = date.today()

        # Calculate date 1 year prior - can change to fit scope
        since_date = today - timedelta(days=365)
        # Convert to iso for api
        iso_date = since_date.isoformat()

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Only want repos updated in last year
        params = {
            "per_page": 100,
            "sort": "updated",
            "since": iso_date
        }

        # Endpoint to get repos for authenticated user
        repos_url = f"{GH_API_URL}/user/repos"

        response = requests.get(url=repos_url, headers=headers, params=params)
        response.raise_for_status()

        repo_data = response.json()

        # Empty dict where we'll get names of repos within params,
        # also get languages for radial chart since in same call
        # can add any other params as empty list we want to use later
        recent = {
            "repo-name": [],
            "language": []
        }

        # Loop through repos in json
        for repo in repo_data:
            # print(f"archived: {repo['archived']} {type(repo['archived'])}")
            # print(f"size: {repo['size']} {type(repo['size'])}")
            # Check repo is not empty, not archived
            if not repo["archived"] and repo["size"] > 0:
                recent["repo-name"].append(repo["name"])
                recent["language"].append(repo["language"])

        # print(f"recent: {recent}")
        return recent

    # def commit_activity(self, user, token, repo_list):
    #     weekly_commits = []
    #     # print(len(repo_list))
    #
    #     headers = {
    #         "accept": "application/vnd.github+json",
    #         "authorization": f"Bearer {token}",
    #         "X-GitHub-Api-Version": "2022-11-28"
    #     }
    #
    #     # make sure list is not empty
    #     if len(repo_list) > 0:
    #         for repo in repo_list:
    #             # Endpoint to get weekly commit count as list, with index 0 being 52 weeks ago
    #             # Problem with this is only counts commits on default branches
    #             weekly_count = f"{GH_API_URL}/repos/{user}/{repo}/stats/participation"
    #
    #             response = requests.get(url=weekly_count, headers=headers)
    #             response.raise_for_status()
    #             data = response.json()
    #
    #             add_activity = {
    #                 repo: data
    #             }
    #
    #             weekly_commits.append(add_activity)
    #     # print(f"weekly commits: {weekly_commits}")
    #     # Sample output with weekly commits numbers
    #     # weekly commits: [{'my-learning': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 42, 10, 29, 32, 34, 19, 6, 7, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 42, 10, 29, 32, 34, 19, 6, 7, 0, 0, 0, 0, 1, 0, 0, 0, 0, 10, 1, 0, 0]}}, {'my-rise': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4]}}, {'dashboard': {'all': [], 'owner': []}}, {'interactive-charting-flask': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0]}}, {'avocado-analytics-dash': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0]}}, {'health-data': {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0], 'owner': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0]}}]
    #     return weekly_commits
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
        repo_list = self.recent_repos["repo-name"]
        print(f"repo list: {repo_list} type: {type(repo_list)}")
        all_repo_events = []

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        params = {
            "per_page": 100
        }

        # TODO: Need to change this to instead look at activity endpoint
        # because even repo by repo only fetches last 90 days
        # TODO: Have to tweak how to get from activity feed bc just says push, no payload count, may hav to fetch this separately
        # make sure list is not empty
        if len(repo_list) > 0:
            for repo in repo_list:
                # Endpoint to get repo activity
                activity_url = f"{GH_API_URL}/repos/{user}/{repo}/activity"

                response = requests.get(url=activity_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                repo_events = {
                    "repo": repo,
                    "ref": [],
                    "date": [],
                    "year": [],
                    "week": [],
                    "month": [],
                    "values": []
                }

                # parse events data per repo
                for event in data:
                    event_type = event["type"]
                    date_str = event["created_at"].strip("Z")
                    event_date = date_str.split("T")[0]
                    created = datetime.fromisoformat(date_str)
                    iso_date = created.isocalendar()
                    # print(f"created: {created} type: {type(created)}")
                    # print(f"date: {date} type: {type(date)}")



                    if event_type == "PushEvent":
                        repo_events["date"].append(event_date)
                        repo_events["year"].append(iso_date.year)
                        repo_events["week"].append(iso_date.week)
                        repo_events["month"].append(created.month)
                        git_ref = event["payload"]["ref"].split("/")[-1]
                        repo_events["ref"].append(git_ref)
                        # repo_events["type"].append(event_type)
                        commits = int(event["payload"]["size"])
                        repo_events["values"].append(commits)

                    # elif event_type == "CreateEvent":
                        # create_type = event["payload"]["ref_type"]
                        # repo_events["payload_target"].append(create_type)
                # Check some push event exists before returning
                if len(repo_events["ref"]) > 0:
                    all_repo_events.append(repo_events)

            print(f"all repo events: {all_repo_events}")
            return all_repo_events
            # # dump output to file for testing
            # with open("recent-repo-events.json", "a") as file:
            #     json.dump(repo_events, file)



