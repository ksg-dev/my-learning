import threading
import time
import random
from flask_login import current_user

from app.github import GetGitHub

class TaskThread(threading.Thread):
    def __init__(self, task_id, app):
        super().__init__()
        self.task_id = task_id
        self.progress = 0
        self.result = None
        self.gh_instance = GetGitHub(user=current_user.name, user_id=current_user.id)
        self.app = app

    #TODO: Working on calling and updating task track here. Operating outside app context, need to fix this
    def run(self):
        total_steps = 3
        with self.app.app_context():
            instance = self.gh_instance

            refresh = instance.refresh_github_data()
            for i in refresh:
                self.progress = i["total_progress"]
                self.result = i["result"]
                print(f"Task {self.task_id}: Progress: {self.progress}  Status: {self.result}")
            self.result = "Task Completed!"

    # def run(self):
    #     # Simulate long-running task
    #     total_steps = random.randint(5, 15)
    #     for i in range(total_steps):
    #         time.sleep(1)
    #         self.progress = (i + 1) * 100 // total_steps
    #         print(f"Task {self.task_id}: Progress: {self.progress}%")
    #     self.result = "Task completed!"

    def update_progress(self, amount):
        self.progress += amount
        return self.progress
        # Step 1: fetch recent repos, no loop, progress 0 or 1
        # result = "Fetching Recent Repos..."
        # Step 2: fetch latest activity, has loop, # is whatever per page for repos
        # result = "Fetching latest activity..."
        # Step 3: fetch commits from shas
        # result = "Fetching commits..."

    def get_progress(self):
        return self.progress

    def get_result(self):
        return self.result


