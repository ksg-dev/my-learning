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

    # TODO: If ALL REPOS call gets 304 Not Modified, return this data for other api calls
    # Need to populate after sha for all repos, next call is to get this sha
    def get_summary_repository_data(self, since_date) -> list[dict]:
        summary_data = []

        select_repos = db.session.execute(db.select(Repository)
                                          .where(Repository.user_id == self.user_id)
                                          .where(Repository.updated_at > since_date)
                                          .order_by(Repository.updated_at.desc())
                                          .limit(10)).scalars().all()

        # Only need repo name and latest activity call etag for outgoing
        for item in select_repos:
            add_repo = {
                "name": item.name,
                "last_activity_etag": item.latest_etag_activity
            }

            summary_data.append(add_repo)

        return summary_data

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

    def update_detail_repo_data(self, data: list[dict]):
        if data:
            for repo in data:
                # Necessary data from latest_shas dict, cleaner to iterate before passing here
                repo_name = repo["repo"]
                after_sha = repo["sha"]
                af_timestamp = repo["timestamp"].strip("Z")
                new_etag = repo["etag"]
                new_timestamp = repo["date"]

                print(f"updating details for: {repo_name}")

                target_repo = db.session.execute(db.select(Repository).where(Repository.name == repo_name)).scalar()

                target_repo.last_called_activity = new_timestamp
                target_repo.latest_etag_activity = new_etag
                target_repo.latest_sha = after_sha
                target_repo.sha_timestamp = datetime.fromisoformat(af_timestamp)

                db.session.commit()



def validate_id(model, ref_id):
    check = db.session.execute(db.select(model).filter_by(id=ref_id)).first()
    return check