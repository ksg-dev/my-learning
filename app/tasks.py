import threading
import time
import random
from app import app

from app.github import GetGitHub

class TaskThread(threading.Thread):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        self.progress = 0
        self.result = None

    def run(self):
        # Simulate long-running task
        total_steps = random.randint(5, 15)
        for i in range(total_steps):
            time.sleep(1)
            self.progress = (i + 1) * 100 // total_steps
            print(f"Task {self.task_id}: Progress: {self.progress}%")
        self.result = "Task completed!"

    def refresh_progress(self):
        # total steps =
        # fetch recent repos, no loop, progress 0 or 1
        # Need call to get recent repos after update by fetch, but before next fetch call.
        # fetch lastest activity, has loop, # is whatever per page for repos

    def get_progress(self):
        return self.progress

    def get_result(self):
        return self.result


