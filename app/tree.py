# Takes GitHub json tree file and structures data for route
from app.events import GetGitHub
from pathlib import PurePath
import json
from treelib import Node, Tree

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
            parent = None

        return parent

    def clean_name(self):
        name = self.path_name.split("/")[-1]

        return name

def generate_dict(data):

    html_parts = []


    for item in data:
        depth = item["path"].count("/")
        indent = "  " * depth
        name = item["path"].split("/")[-1]
        if item["type"] == "blob":
            html_parts.append(f"{indent}<i class='bi bi-file-earmark-code'> {name}</i>")
        else:
            html_parts.append(f"{indent}<i class='bi bi-folder'> {name}</i>")

    # html_parts.append("</pre>")
    # html_content = "\n".join(html_parts)
    # print(html_parts)

    for i in html_parts:
        print(i)
    # return html_content

def generate_tree(data, repo):
    # Takes API json data and formats each as TreeObject

    ftree = Tree()
    ftree.create_node(f"{repo} /", f"{repo}")

    for item in data:
        pathname = item["path"]
        obj_type = item["type"]


        new_obj = TreeObject(path_name=pathname, obj_type=obj_type)
        if new_obj.parent is None:
            new_obj.parent = repo


        check_node = ftree.get_node(new_obj.name)
        if not check_node:
            ftree.create_node(new_obj.name, new_obj.name, parent=new_obj.parent, data=new_obj)

    return ftree.show(stdout=False)

# gh = GetGitHub("ksg-dev")
# tree = gh.get_tree(REPO)
# print(generate_tree(tree, REPO))
# generate_dict(tree)


