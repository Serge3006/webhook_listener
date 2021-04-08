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

names_mapping = {"bimerr-occupant-behavior": "occupancy-profile",
                 "bimerr-kpi": "key-performance-indicator",
                 "bimerr-senML": "sensor-data",
                 "bimerr-building": "building",
                 "bimerr-material-properties": "material-properties",
                 "bimerr-renovation-measures": "renovation-measures",
                 "bimerr-metadata": "metadata",
                 "bimerr-annotation-objects": "annotation-objects",
                 "bimerr-information-objects": "information-objects",
                 "bimerr-renovation-process": "renovation-process",
                 "bimerr-weather": "weather"}


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


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
        if repo_name != "bimerr-website":
            folder_name = names_mapping[repo_name]

        repos_path = os.path.join(os.path.dirname(os.getcwd()), "repos")

        git_repo = os.path.join(repos_path, repo_name)
        g = git.cmd.Git(git_repo)
        g.pull()

        # In this repo is the information I want to send to the server
        if repo_name != "bimerr-website":
            git_repo_documentation = os.path.join(git_repo, "documentation")
        else:
            git_repo_documentation = git_repo
        transport = paramiko.Transport(("192.168.122.109", 80))
        transport.connect(username="bimerr", password="password")
        sftp = MySFTPClient.from_transport(transport, banner_timeout=200)
        if repo_name != "bimerr-website":
            dst_dir = "/var/www/html/def/" + folder_name
        else:
            dst_dir = "/var/www/html"
        sftp.mkdir(dst_dir, ignore_existing=True)
        sftp.put_dir(git_repo_documentation, dst_dir)
        sftp.close()

        return "Success"

@app.route("/", methods=["GET"])
def home():
    return "<h1>App running</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
