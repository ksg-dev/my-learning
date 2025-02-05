# Responsible for communicating w GitHub API, formatting events data
import os
from dotenv import load_dotenv
import requests
from requests import HTTPError
from github import Github, Auth

from app import app, db
from app.models import Event, Repository
from datetime import datetime
from pprint import pprint

load_dotenv()

GH_TOKEN = os.environ["GITHUB_TOKEN"]
GH_USERNAME = os.environ["GITHUB_USERNAME"]

GH_API_URL = "https://api.github.com"

class GetGitHub:
    def __init__(self, user, bulk=False):
        self.user = user
        self.token = GH_TOKEN
        self.bulk = bulk
        self.events = self.get_events(user, bulk)
        self.repos = self.get_repos(user, bulk)


    def get_events(self, user, bulk):
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if bulk is True:
            params = {
                "per_page": 100
            }
        else:
            params = {
                "per_page": 50
            }

        user_events = f"{GH_API_URL}/users/{user}/events"

        response = requests.get(url=user_events, headers=headers, params=params)
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
                    "action": f"Pushed {commits} commit(s) to {repo}"
                }

                # new_event = {
                #     "id": i["id"],
                #     "type": "push",
                #     "repo": i["repo"]["name"].split("/")[1],
                #     "repo_id": i["repo"]["id"],
                #     "commits": i["payload"]["size"],
                #     "create_type": None,
                #     "timestamp": i["created_at"].strip("Z")
                # }

            elif i["type"] == "CreateEvent":
                create_type = i["payload"]["ref_type"]
                event = {
                    "timestamp": datetime.fromisoformat(event_timestamp),
                    "action": f"Created {create_type} in {repo}"
                }

                # new_event = {
                #     "id": i["id"],
                #     "type": "create",
                #     "repo": i["repo"]["name"].split("/")[1],
                #     "repo_id": i["repo"]["id"],
                #     "commits": None,
                #     "create_type": i["payload"]["ref_type"],
                #     "timestamp": i["created_at"].strip("Z")
                # }

            all_events.append(event)

        # print(f"all_events: {all_events}")
        return all_events


    def get_repos(self, user, bulk):
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if bulk is True:
            params = {
                "per_page": 100
            }
        else:
            params = {
                "per_page": 50
            }

        user_repos = f"{GH_API_URL}/users/{user}/repos"


        response = requests.get(url=user_repos, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json()

        all_repos = []

        for repo in repos:
            # default_branch = repo["default_branch"]
                # repo_name = repo["name"]
                # get_sha = f"{GH_API_URL}repos/{GH_USERNAME}/{repo_name}/git/ref/heads/{default_branch}"
                #
                # sha_response = requests.get(url=get_sha, headers=headers)
                # sha_response.raise_for_status()
                # data = sha_response.json()
                # sha = data["object"]["sha"]


            new_repo = {
                "id": int(repo["id"]),
                "name": repo["name"],
                "created": repo["created_at"],
                "language": repo["language"]
            }
            # print(new_repo)

            all_repos.append(new_repo)

        return all_repos

    def get_tree(self, repo):
        user = self.user
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        params = {
            "recursive": True
        }

        # Get repo data for default branch
        get_repo = f"{GH_API_URL}repos/{user}/{repo}"
        repo_response = requests.get(url=get_repo, headers=headers)
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        default_branch = repo_data["default_branch"]

        # Get sha reference
        get_sha = f"{GH_API_URL}/repos/{user}/{repo}/git/ref/heads/{default_branch}"

        sha_response = requests.get(url=get_sha, headers=headers)
        sha_response.raise_for_status()
        data = sha_response.json()
        sha = data["object"]["sha"]

        # Get tree
        get_tree = f"{GH_API_URL}/repos/{user}/{repo}/git/trees/{sha}"

        # tree_root = requests.get(url=get_tree, headers=headers)
        tree_response = requests.get(url=get_tree, headers=headers, params=params)
        # tree_root.raise_for_status()
        tree_response.raise_for_status()
        # troot = tree_root.json()["tree"]
        tree = tree_response.json()["tree"]

        # print(f"************")
        # print(tree)
        return tree

    def get_feed(self):
        user = self.user
        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Get all available feeds
        get_feeds = f"{GH_API_URL}/feeds"

        response = requests.get(url=get_feeds, headers=headers)
        response.raise_for_status()
        all_feeds = response.json()
        user_feed = f"{all_feeds['user_url']}"

        print(all_feeds)

        print(user_feed)
        # clipped = user_feed.strip(".atom")
        # print(clipped)

        # Request for user-specific feed
        # user_feed = requests.get(url=user_feed)
        # user_feed.raise_for_status()
        # my_feed = user_feed.json()

        # print(my_feed)



def validate_id(model, ref_id):
    check = db.session.execute(db.select(model).filter_by(id=ref_id)).first()
    return check


# gh = GetGitHub(GH_USERNAME)
# gh.get_feed()