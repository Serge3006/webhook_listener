import os
import flask
from flask import request
import git
import shutil
import paramiko
from distutils.dir_util import copy_tree
import socket

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route("/webhook", methods=["POST"])
def github_webhook():

    if request.headers["Content-Type"] == "application/json":
        content = request.json
        repo_name = content["repository"]["name"]
        source_path = ""
        dst_path = ""

        git_repo = os.path.join(source_path, repo_name)
        g = git.cmd.Git(git_repo)
        g.pull()

        os.makedirs(dst_path, exist_ok=True)
        os.system("cp -r {} {}".format(dst_path, dst_path))

        return "Success"

@app.route("/", methods=["GET"])
def home():
    return "<h1>App running</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
