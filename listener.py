import os
import flask
from flask import request
import git
import shutil
import paramiko
from distutils.dir_util import copy_tree

app = flask.Flask(__name__)
app.config["DEBUG"] = True

names_mapping = {"bimerr-occupant-behavior": "occupancy-profile",
                 "bimerr-kpi": "key-performance-indicator",
                 "bimerr-senML": "sensor-data"}


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
        folder_name = names_mapping[repo_name]

        repos_path = os.path.join(os.path.dirname(os.getcwd()), "repos")

        git_repo = os.path.join(repos_path, repo_name)
        g = git.cmd.Git(git_repo)
        g.pull()

        # In this repo is the information I want to send to the server
        git_repo_documentation = os.path.join(git_repo, "documentation")

        transport = paramiko.Transport(("oeg4.dia.fi.upm.es", 22))
        transport.connect(username="schavez", password="password")
        sftp = MySFTPClient.from_transport(transport)
        dst_dir = "/opt/web/bimerr.iot.linkeddata.es/def/" + folder_name
        sftp.mkdir(dst_dir, ignore_existing=True)
        sftp.put_dir(git_repo_documentation, dst_dir)
        sftp.close()

        return "Success"

@app.route("/webhook", methods=["GET"])
def home():
    return "<h1>App running</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
