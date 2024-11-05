# Takes GitHub json tree file and structures data for route
from app.events import GetGitHub
from pathlib import PurePath
import json
from treelib import Node, Tree

REPO = "tic-tac-toe"

class TreeObject:
    def __init__(self, path_name, obj_type):
        self.path_name = path_name
        self.obj_type = obj_type
        self.name = self.clean_name()
        self.parent = self.get_parent()
        # self.sha = sha
        # self.url = url

    def get_parent(self):
        path_check = self.path_name.split("/")

        if len(path_check) > 1:
            parent = path_check[-2]

        else:
            parent = REPO

        return parent

    def clean_name(self):
        name = self.path_name.split("/")[-1]

        return name



def generate_tree(data, repo):
    # Takes API json data and formats each as TreeObject

    ftree = Tree()
    ftree.create_node(f"{repo} /", f"{repo}")

    for item in data:
        pathname = item["path"]
        obj_type = item["type"]


        new_obj = TreeObject(path_name=pathname, obj_type=obj_type)


        check_node = ftree.get_node(new_obj.name)
        if not check_node:
            ftree.create_node(new_obj.name, new_obj.name, parent=new_obj.parent, data=new_obj)

    return ftree.show(stdout=False)

gh = GetGitHub("ksg-dev")
tree = gh.get_tree(REPO)
print(generate_tree(tree, REPO))


