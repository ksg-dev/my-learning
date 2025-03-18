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

    # Get recent repos at once for initial get call...
    # Will still need separate calls to exist though for separate db calls to get
    # after each fetch so next call in chain is working with newest updated data
    def get_recent_repos_data(self, since_date, limit) -> list[dict]:
        summary_data = []

        select_repos = db.session.execute(db.select(Repository)
                                          .where(Repository.user_id == self.user_id)
                                          .where(Repository.updated_at > since_date)
                                          .order_by(Repository.updated_at.desc())
                                          .limit(limit)).scalars().all()

        for repo in select_repos:
            add_repo = {
                "name": repo.name,
                "last_activity_etag": repo.latest_etag_activity,
                "sha": repo.latest_sha,
                "etag": repo.commits_etag,
                "data": repo.commits_data
            }

            summary_data.append(add_repo)

        return summary_data

    # Use this call for repos list for later api calls If ALL REPOS call gets 304 Not Modified,
    # OR to get latest data added to db to give back to next API call
    # Need to populate after sha for all repos, next call is to get this sha
    def get_summary_repository_data(self, since_date, limit) -> list[dict]:
        summary_data = []

        select_repos = db.session.execute(db.select(Repository)
                                          .where(Repository.user_id == self.user_id)
                                          .where(Repository.updated_at > since_date)
                                          .order_by(Repository.updated_at.desc())
                                          .limit(limit)).scalars().all()

        # Only need repo name and latest activity call etag for outgoing
        for item in select_repos:
            add_repo = {
                "name": item.name,
                "last_activity_etag": item.latest_etag_activity
            }

            summary_data.append(add_repo)

        return summary_data

    # Get latest activity shas for all repos for commit call, used after fetch latest shas
    def get_repository_sha_data(self, since_date, limit) -> list[dict]:
        activity_shas = []

        select_repos = db.session.execute(db.select(Repository)
                                          .where(Repository.user_id == self.user_id)
                                          .where(Repository.updated_at > since_date)
                                          .order_by(Repository.updated_at.desc())
                                          .limit(limit)).scalars().all()

        # Only need repo name and latest sha and commits etag for outgoing to commits
        for item in select_repos:
            add_repo = {
                "name": item.name,
                "sha": item.latest_sha,
                "etag": item.commits_etag
            }

            activity_shas.append(add_repo)

        return activity_shas
    #
    # # Get commits json data for all repos for dashboard stats
    # def get_commit_data(self, recent_repos) -> list[dict]:
    #     commits_data = []
    #
    #     # select_repos = db.session.execute(db.select(Repository)
    #     #                                   .where(Repository.user_id == self.user_id)
    #     #                                   .where(Repository.updated_at > since_date)
    #     #                                   .order_by(Repository.updated_at.desc())
    #     #                                   .limit(75)).scalars().all()
    #
    #     # Create list of dicts for Dashboard analytics
    #     for item in select_repos:
    #         add_data = {
    #             "name": item.name,
    #             "data": item.commits_data
    #         }
    #
    #         commits_data.append(add_data)
    #
    #     return commits_data

    # If ALL REPOS call gets 200, parse json and store necessary data
    def update_summary_repository_data(self, data):
        if data:
            for repo in data:
                # Necessary data from json
                repo_id = repo["id"]
                repo_name = repo["name"]
                repo_created = repo["created_at"].strip("Z")
                repo_updated = repo["updated_at"].strip("Z")
                repo_pushed = repo["pushed_at"].strip("Z")

                # first check if repo needs to be added
                check_exists = validate_id(Repository, repo_id)

                if check_exists is None:
                    new_repo = Repository(
                        id=repo_id,
                        name=repo_name,
                        created_at=datetime.fromisoformat(repo_created),
                        updated_at=datetime.fromisoformat(repo_updated),
                        pushed_at=datetime.fromisoformat(repo_pushed),
                        user_id=self.user_id
                    )

                    db.session.add(new_repo)
                    db.session.commit()

                # If repo exists in db, check if any data needs to be updated
                else:
                    target_repo = db.get_or_404(Repository, repo_id)

                    if not target_repo.created_at:
                        target_repo.created_at = datetime.fromisoformat(repo_created)
                    if target_repo.updated_at != datetime.fromisoformat(repo_updated):
                        target_repo.updated_at = datetime.fromisoformat(repo_updated)
                    if target_repo.pushed_at != datetime.fromisoformat(repo_pushed):
                        target_repo.pushed_at = datetime.fromisoformat(repo_pushed)

                    db.session.commit()

    # If get_latest_activity returns 200 or 304 - update repo details in db
    def update_detail_repo_data(self, data: list[dict]):
        if data:
            for repo in data:
                # Necessary data from latest_shas dict
                # Data from 200 and 304s
                repo_name = repo["repo"]
                new_etag = repo["etag"]
                new_timestamp = repo["date"]

                print(f"updating details for: {repo_name}")

                target_repo = db.session.execute(db.select(Repository).where(Repository.name == repo_name)).scalar()

                target_repo.last_called_activity = new_timestamp
                target_repo.latest_etag_activity = new_etag

                # Data for 200 responses
                after_sha = repo["activity"]["sha"]
                if after_sha:
                    af_timestamp = repo["activity"]["timestamp"].strip("Z")

                    target_repo.latest_sha = after_sha
                    target_repo.sha_timestamp = datetime.fromisoformat(af_timestamp)

                db.session.commit()

    def update_commit_data(self, data: list[dict]):
        if data:
            for repo in data:
                # Data from 200
                repo_name = repo["repo"]
                commits_etag = repo["commits_etag"]
                data = repo["com_data"]

                print(f"updating commits for: {repo_name}")

                target_repo = db.session.execute(db.select(Repository).where(Repository.name == repo_name)).scalar()

                target_repo.commits_etag = commits_etag
                target_repo.commits_data = data

                db.session.commit()



def validate_id(model, ref_id):
    check = db.session.execute(db.select(model).filter_by(id=ref_id)).first()
    return check