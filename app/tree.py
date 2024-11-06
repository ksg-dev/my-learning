# Takes GitHub json tree file and structures data for route
from github import Github, Auth
from dotenv import load_dotenv
import os

# load_dotenv()

GH_TOKEN = os.environ["GITHUB_TOKEN"]
# GH_USERNAME = os.environ["GITHUB_USERNAME"]


def make_tree(username, repo_name):
    # Authenticate w token
    auth = Auth.Token(GH_TOKEN)

    # Pygithub object
    g = Github(auth=auth)

    # Get user by username
    user = g.get_user(username)

    # Get repo contents recursively
    repo = g.get_repo(f"{username}/{repo_name}")
    contents = repo.get_contents("")
    tree = {
        'name': 'root',
        'children': []
    }

    while contents:
        file_content = contents.pop(0)
        segments = file_content.path.split("/")
        depth = len(segments)
        name = segments[-1]
        if depth > 1:
            parent = segments[-2]
        else:
            parent = "root"

        if parent == tree["name"]:
            tree["children"].append({
                'name': name,
                'children': []
            })

        elif depth == 2:
            for entry in tree["children"]:
                if parent == entry["name"]:
                    entry["children"].append({
                        'name': name,
                        'children': []
                    })

        elif depth > 2:
            for entry in tree["children"]:
                # print(f"entry: {entry}")
                # for key, value in entry.items():
                    # print(f"key: {key} value: {value}")
                if entry["name"] == segments[-3]:
                    entry["children"].append(
                        {
                            'name': segments[-3],
                            'children': [
                                {
                                    'name': name,
                                    'children': []
                                }]
                            }
                    )



        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))

        # print(file_content)

    return tree
