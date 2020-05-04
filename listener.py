import os
import flask
from flask import request
import git
import shutil
from distutils.dir_util import copy_tree

app = flask.Flask(__name__)
app.config["DEBUG"] = True

names_mapping = {"bimerr-occupant-behavior": "occupancy-profile",
                 "bimerr-kpi": "key-performance-indicator",
                 "bimerr-senML": "sensor-data"}

def copy_files(source, dest):

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

@app.route("/webhook/post", methods=["POST"])
def github_webhook():

    if request.headers["Content-Type"] == "application/json":
        content = request.json
        repo_name = content["repository"]["name"]
        folder_name = names_mapping[repo_name]

        repos_path = os.path.join(os.path.dirname(os.getcwd()), "repos")
        domains_path = os.path.join(os.getcwd(), "domains")

        #html_documentation = os.path.join(domains_path, folder_name)
        git_repo = os.path.join(repos_path, repo_name)
        g = git.cmd.Git(git_repo)
        g.pull()

        # In this repo is the information I want to send to the server
        git_repo_documentation = os.path.join(git_repo, "documentation")
        #copy_files(git_repo_documentation, html_documentation)
        #copy_tree(git_repo_documentation, html_documentation)

        return "Success"

@app.route("/webhook", methods=["GET"])
def home():
    return "<h1>App running</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
