# Responsible for communicating w GitHub API formatting data
import os
from dotenv import load_dotenv
import requests

from app import app, db
from app.data_manager import DataManager
from datetime import datetime, date, timedelta
from pprint import pprint
import json


load_dotenv()

GH_API_URL = "https://api.github.com"


class GetGitHub:
    """Functions starting w FETCH call API, starting w GET pull data from db via DataManager"""
    def __init__(self, user, user_id):
        self._user = user
        self._token = os.environ["GITHUB_TOKEN"]
        self.user_id = user_id
        self.data_manager = DataManager(self._user, self.user_id)
        self.recent_repos = self.get_github_data()


    # TODO: Button to refresh data as async request....want to add a progress bar for call progress
    # Method to refresh API data
    def refresh_github_data(self, since: timedelta = timedelta(days=365), per_page=100):
        data = {
            "total_progress": 0,
            "result": "Refreshing..."
        }
        # Get todays date
        today = date.today()
        # Calculate since date, default 1 year prior
        since_date = today - since

        # fetch recent repos, update db
        self.fetch_recent_repos_(since_date=since_date, per_page=per_page)
        data["total_progress"] += 20
        data["result"] = "Fetching latest activity.."
        yield data
        # New call to db via Datamanager to get recent repos after fetch
        repo_list = self.data_manager.get_summary_repository_data(since_date=since_date, limit=per_page)
        # fetch latest activity shas with updated repo_list
        self.fetch_latest_activity_sha(repo_list=repo_list)
        data["total_progress"] += 40
        data["result"] = "Fetching Commits.."
        yield data
        # New call to db via DataManager to get recent shas after fetch
        repo_shas = self.data_manager.get_repository_sha_data(since_date=since_date, limit=per_page)
        # fetch latest commits with updated activity shas
        self.fetch_commits_from_sha(repo_shas=repo_shas, per_page=per_page)
        data["total_progress"] += 40
        data["result"] = "All Done!.."
        yield data
        # Once all are fetched, get all data
        self.get_github_data()

    def get_github_data(self, since: timedelta = timedelta(days=365), per_page=100):
        # Get todays date
        today = date.today()
        # Calculate since date, default 1 year prior
        since_date = today - since

        # Get repos data via Data Manager
        repo_data = self.data_manager.get_recent_repos_data(since_date=since_date, limit=per_page)

        return repo_data

    # Cleaning commit data for charting and dashboard
    def clean_commit_data(self):
        repo_data = self.recent_repos
        clean_commits_data = {
            "repo": [],
            "timestamps": []
        }

        for repo in repo_data:
            commit_data = repo["data"]
            if commit_data:
                for i in commit_data:
                    date_str = i["commit"]["author"]["date"].strip("Z")
                    timestamp = datetime.fromisoformat(date_str)

                    clean_commits_data["repo"].append(repo["name"])
                    clean_commits_data["timestamps"].append(timestamp)

        return clean_commits_data

    def fetch_events(self):
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {
                "per_page": 100
            }

        user_events = f"{GH_API_URL}/users/{self._user}/events"

        response = requests.get(url=user_events, headers=headers, params=payload)
        response.raise_for_status()

        events = response.json()

        all_events = []

        for i in events:
            event = {}
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

        return all_events

    # STEP 1: Make API call to endpoint for list of repos for authenticated user updated in the last year,
    # conditional header for if none match etag
    def fetch_recent_repos_(self, since_date, per_page):
        # yield {'result': 'Fetching Recent Repos...'}
        print(f"Calling Recent Repos....")
        # call with no etag to start to populate...
        # etag = None
        etag = self.data_manager.etag

        # Convert to iso for api
        iso_date = since_date.isoformat()

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if etag:
            headers["if-none-match"] = etag

        # Set params around since and per page, default 1 year and per page 100
        params = {
            "per_page": per_page,
            "sort": "updated",
            "since": iso_date
        }

        # Endpoint to get repos for authenticated user
        repos_url = f"{GH_API_URL}/user/repos"

        response = requests.get(url=repos_url, headers=headers, params=params)
        response.raise_for_status()

        # Even if etag stays the same, need to update last called date
        new_etag = response.headers["etag"]
        new_date = datetime.now()

        print(f"Recent repos response returned: {response.status_code}")

        # If successful, want to update repo data in db first
        if response.status_code == 200:
            # self.recent_repos_data = response.json()
            self.data_manager.update_summary_repository_data(response.json())
        # just for testing, may be able to eliminate
        elif response.status_code == 304:
            print(f"Not Modified: {response.headers}")

        # After updating db with any new repo data, update etag, timestamp for user
        self.data_manager.set_user_etag(etag=new_etag, timestamp=new_date)

    # STEP 2 : Loop through recent repo data, for each repo name, call activity api and get latest "after" sha,
    # conditional etag header
    def fetch_latest_activity_sha(self, repo_list):
        latest_shas = []

        headers = {
                "accept": "application/vnd.github+json",
                "authorization": f"Bearer {self._token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

        # Limit to only single most recent activity for repo
        params = {
            "per_page": 1
        }

        # Check for data
        if repo_list:
            # Loop through each repo in recent repo data
            for repo in repo_list:

                # Repo Name
                repo_name = repo["name"]
                # Latest Activity ETag

                if repo["last_activity_etag"]:
                    headers["if-none-match"] = repo["last_activity_etag"]

                # Endpoint to get detailed repo activity
                activity_url = f"{GH_API_URL}/repos/{self._user}/{repo_name}/activity"

                response = requests.get(url=activity_url, headers=headers, params=params)
                response.raise_for_status()
                print(f"activity call for {repo_name} returned: {response.status_code}")
                # data = response.json()

                # Even if etag stays the same, need to update last called date
                new_etag = response.headers["etag"]
                new_date = datetime.now()

                # If successful, want to update repo data in db first
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        sha_data = {
                            "repo": repo_name,
                            "etag": new_etag,
                            "date": new_date,
                            "activity": {
                                "sha": data[0]["after"],
                                "timestamp": data[0]["timestamp"]
                            }
                        }

                        latest_shas.append(sha_data)

                elif response.status_code == 304:
                    sha_data = {
                        "repo": repo_name,
                        "etag": new_etag,
                        "date": new_date,
                        "activity": {
                            "sha": None,
                            "timestamp": None
                        }
                    }

                    latest_shas.append(sha_data)

                else:
                    continue

            # Call to update repo detail w Data Manager
            print(f"Calling update details...")
            self.data_manager.update_detail_repo_data(data=latest_shas)

    #  STEP 3: Take AFTER sha from step 2, make call to commits for repo endpoint,
    #  with "sha" query param set to AFTER sha, per_page=100.
    def fetch_commits_from_sha(self, repo_shas, per_page):
        commits_data = []

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check for data
        if repo_shas:
            # Loop through each repo/sha in latest shas
            for repo in repo_shas:
                # Get repo name
                repo_name = repo["name"]
                latest_sha = repo["sha"]

                # E-Tag for commit data currently in db, in any
                if repo["etag"]:
                    headers["if-none-match"] = repo["etag"]

                # Pass latest sha as param so doesn't just use default branch
                # Setting per page to 10 for testing
                params = {
                    "per_page": per_page,
                    "sha": latest_sha
                }

                # Endpoint to get commits w sha to start listing from
                commits_url = f"{GH_API_URL}/repos/{self._user}/{repo_name}/commits"

                response = requests.get(url=commits_url, headers=headers, params=params)
                response.raise_for_status()

                print(f"commits call for {repo_name} returned: {response.status_code}")

                # If successful 200, get json data, update db
                if response.status_code == 200:
                    data = response.json()
                    new_etag = response.headers["etag"]

                    new_commits = {
                        "repo": repo_name,
                        "commits_etag": new_etag,
                        "com_data": data
                    }

                    commits_data.append(new_commits)
                # No need to store anything if 304, so else continue loop
                else:
                    continue

            # Call to update commit data w Data Manager
            self.data_manager.update_commit_data(data=commits_data)

    def get_repo_languages(self):
        all_langs = []

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check for data
        if self.recent_repos:
            # Loop through each repo in recent repo data
            for repo in self.recent_repos:
                # Get repo name
                repo_name = repo["name"]

                # Endpoint to get detailed repo language breakdown
                lang_url = f"{GH_API_URL}/repos/{self._user}/{repo_name}/languages"

                response = requests.get(url=lang_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                all_langs.append(data)

            # dump to json for testing
            with open("repo-languages.json", "a") as file:
                json.dump(all_langs, file)

        return all_langs

