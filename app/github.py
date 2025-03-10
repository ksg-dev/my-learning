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
    def __init__(self, user, user_id):
        self._user = user
        self._token = os.environ["GITHUB_TOKEN"]
        self.user_id = user_id
        self.data_manager = DataManager(self._user, self.user_id)
        self.events = self.get_events(user=self._user, token=self._token)
        # If recent_repos call receives data, json stored
        self.recent_repos_data = self.get_recent_repos_list()
        self.my_latest_shas = self.get_latest_activity_sha(user=self._user, token=self._token)
        # self.get_commits = self.get_recent_repo_commits()
        # Testing new commits func using sha output
        self.commits_data = self.get_commits_from_sha(user=self._user, token=self._token)
        self.languages = self.get_repo_languages(user=self._user, token=self._token)
        # self.repo_activity = self.recent_repo_activity(user=self._user, token=self._token)
        # self.py_data = self.pygithub_get_commits(token = self._token, user=self._user)
    """
    For recent repos commits....
    
    STEP 1: 
    >>Store etag of last call in user table for if-none-match header
        List all repos for auth user using since param to only show those updated in last year/whatever time period.
        
    STEP 2: 
    >>Store E-tag and latest sha for each repo in repo table
        Take output json from list all repos, loop through response data -- for each repo-name, make call to List Repo Activity
        endpoint, limit activity with per_page=1 so it will only return latest activity. Get "after" value (latest sha). 
        
    STEP 3:
        Take AFTER sha from step 2, make call to commits for repo endpoint, with "sha" query param set to AFTER sha, per_page=100.
        This will give a list of all commits from your latest commit sha (even if not on main branch) going backwards 
        (so will include other branches as it follows sha refs backwards)
    
    STEP 4:
        Now can take that commit data for each repo and get date of commits and group however
    
    """
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

    # STEP 1: Make API call to endpoint for list of repos for authenticated user updated in the last year, conditional header for if none match etag
    def get_recent_repos_list(self):
        print(f"Calling Recent Repos....")
        # call with no etag to start to populate...
        etag = None
        # etag = self.data_manager.etag


        # Get today's date
        today = date.today()

        # Calculate date 1 year prior - can change to fit scope
        since_date = today - timedelta(days=365)
        # Convert to iso for api
        iso_date = since_date.isoformat()

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        if etag:
            headers["if-none-match"] = etag

        # Only want repos updated in last year - let's cap at 75 for performance
        params = {
            "per_page": 5,
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

        if response.status_code == 200:
            self.recent_repos_data = response.json()
            self.data_manager.update_summary_repository_data(response.json())
            # print(f"new_etag: {new_etag} - {type(new_etag)}")
            # print(f"new_date: {new_date} - {type(new_date)}")
            self.data_manager.set_user_etag(etag=new_etag, timestamp=new_date)
            # return self.recent_repos_data
        elif response.status_code == 304:
            print(f"Not Modified: {response.headers}")
            # if no changes, get formatted repo data from data manager get function and return that for other api calls


        # Returns json of list of repos updated in last year
        # return self.recent_repos_data

    # STEP 2 : Loop through recent repo data, for each repo name, call activity api and get latest "after" sha
    def get_latest_activity_sha(self, user, token):
        latest_shas = []

        headers = {
                "accept": "application/vnd.github+json",
                "authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

        # Limit to only single most recent activity for repo
        params = {
            "per_page": 1
        }

        # Check for data
        if self.recent_repos_data:
            # Loop through each repo in recent repo data
            for repo in self.recent_repos_data:
                # Get repo name
                repo_name = repo["name"]

                # Endpoint to get detailed repo activity
                activity_url = f"{GH_API_URL}/repos/{user}/{repo_name}/activity"

                response = requests.get(url=activity_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()


                if len(data) > 0:
                    add_sha = {
                        "repo": repo_name,
                        "sha": data[0]["after"]
                    }

                    latest_shas.append(add_sha)

            # dump output to file for testing - remember changed max repos to 10 for testing
            # with open("latest_shas.json", "a") as file:
            #     json.dump(latest_shas, file)
            return latest_shas

    #   STEP 3: Take AFTER sha from step 2, make call to commits for repo endpoint, with "sha" query param set to AFTER sha, per_page=100.
    def get_commits_from_sha(self, user, token):
        commits = {
            'timestamps': [],
            'repo': []
        }

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check for data
        if self.my_latest_shas:
            # Loop through each repo/sha in latest shas
            for repo in self.my_latest_shas:
                # Get repo name
                repo_name = repo["repo"]
                latest_sha = repo["sha"]

                # Expand per_page param to 100, and pass latest sha as param so doesn't just use default branch
                # Setting per page to 10 for testing
                params = {
                    "per_page": 100,
                    "sha": latest_sha
                }

                # Endpoint to get commits w sha to start listing from
                commits_url = f"{GH_API_URL}/repos/{user}/{repo_name}/commits"

                response = requests.get(url=commits_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                dates = []

                # Check for commit data, think it'll be easier to loop here for just the data we need - date, repo, commit
                if len(data) > 0:
                    for i in data:
                        # date_str = i["commit"]["author"]["date"].strip("Z")
                        # timestamp = datetime.fromisoformat(date_str)

                        timestamp = date_str = i["commit"]["author"]["date"]

                        # dates.append(timestamp)

                        commits["timestamps"].append(timestamp)
                        commits["repo"].append(repo_name)


                    # commits[repo_name] = pd.Series(dates)

                    # commits.append(add_commits)
            # This was dump with repo: data for testing
            # with open("commits-from-sha.json", "a") as file:
            #     json.dump(commits, file)

            # with open("commits_clean.json", "a") as file:
            #     json.dump(commits, file)
        # print(commits)
        return commits

    def get_repo_languages(self, user, token):
        all_langs = []

        headers = {
            "accept": "application/vnd.github+json",
            "authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check for data
        if self.recent_repos_data:
            # Loop through each repo in recent repo data
            for repo in self.recent_repos_data:
                # Get repo name
                repo_name = repo["name"]

                # Endpoint to get detailed repo language breakdown
                lang_url = f"{GH_API_URL}/repos/{user}/{repo_name}/languages"

                response = requests.get(url=lang_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                all_langs.append(data)

            # dump to json for testing
            with open("repo-languages.json", "a") as file:
                json.dump(all_langs, file)

        return all_langs






    #   def recent_repo_activity(self, user, token):
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

    # Problem with this, shows push but not payload/commits count
    #
    #             add_activity = {
    #                 repo: data
    #             }
    #
    #             repo_activity.append(add_activity)
    #         # dump output to file for testing
    #         with open("recent-repo-activity.json", "a") as file:
    #             json.dump(repo_activity, file)
    def get_recent_repo_commits(self):
        repo_data = self.recent_repos_data

        for i in repo_data:
            commit_url = i["commits_url"]

            response = requests.get(commit_url)
            response.raise_for_status()
            data = response.json()

            # dump output to file for testing
            with open("repo_to_commit_url.json", "a") as file:
                json.dump(data, file)

    def get_repo_names_lang(self):

        """
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
        """
        pass

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
    #

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



