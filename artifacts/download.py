#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# wget https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/a/axel-2.4-9.el7.x86_64.rpm
# rpm -ivh  axel-2.4-9.el7.x86_64.rpm
import os
import re
import subprocess
import sys
from typing import List

import yaml


class DownloadHelper(object):
    def __init__(self):
        self.repo_ip = "repo.datacanvas.com"
        self.repo_user = "dingorouser"
        self.repo_password = "AP82gDSNh12xjjuGQeKztnBzuth"
        self.repo_url = "http://{}:8081/artifactory".format(self.repo_ip)
        self.repo_meta_url = "http://{}:8081/artifactory/ui/artifactgeneral".format(self.repo_ip)
        self.repo_name = "dingo-snapshot"
        self.repo_path = "artifact/common"


    def download(self, path_in_repo: str, local_file: str, progress=""):
        path_in_repo = os.path.join(self.repo_path, path_in_repo)
        download_url = "{}/{}/{}".format(self.repo_url, self.repo_name, path_in_repo)
        star_count = 50
        print("#" * star_count)
        print("# {} {}".format(progress, path_in_repo))
        print("# " + download_url)
        print("#   => " + local_file)
        print("#" * star_count)
        while self.__need_download(path_in_repo, local_file):
            if self.__cmd_exists("axel"):
                self.__axel_cmd(download_url, local_file, self.repo_user, self.repo_password)
            else:
                print("Please install axel!")
                sys.exit(1)
            if not self.__validate_download(path_in_repo, local_file):
                print("Validation failed, download again.")
                print()
            else:
                print("Validation OK.")
                break
        print("-" * star_count)
        print()

    def __need_download(self, path_in_repo, local_file):
        if path_in_repo and os.path.isfile(local_file):
            local_file_checksum = self.__get_sha1_of_local_file(local_file)
            remote_file_checksum = ''
            # noinspection PyBroadException
            try:
                remote_file_checksum = self.__get_sha1_of_remote_file(self.repo_name, path_in_repo)
            except Exception:
                print("Failed to fetch remote file info.")

            if local_file_checksum != remote_file_checksum:
                print("File checksum does not match, download again.")
                print()
                return True
            else:
                print("local_file_checksum:", local_file_checksum)
                print("remote_file_checksum: ", remote_file_checksum)
                print("File already exists. ")
                return False
        else:
            print("Local file does not exist.")
        print("Downloading to " + local_file)
        return True

    def __validate_download(self, path_in_repo, local_file):
        print("Validating local file " + local_file)
        if path_in_repo and os.path.isfile(local_file):
            local_file_checksum = self.__get_sha1_of_local_file(local_file)
            remote_file_checksum = ''
            # noinspection PyBroadException
            try:
                remote_file_checksum = self.__get_sha1_of_remote_file(self.repo_name, path_in_repo)
            except Exception:
                print("Failed to fetch remote file info.")
            return local_file_checksum == remote_file_checksum
        return False

    def __get_sha1_of_remote_file(self, repo_name, path_in_repo):
        import urllib3
        import json

        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth="{}:{}".format(self.repo_user, self.repo_password))
        headers['Content-Type'] = 'application/json'
        data = {"type": "file", "repoKey": repo_name, "path": path_in_repo}
        encoded_data = json.dumps(data).encode('utf-8')
        response = http.request('POST', self.repo_meta_url, body=encoded_data, headers=headers)
        result = json.loads(response.data.decode("utf-8"))

        return result.get('checksums').get('sha1Value')

    def __get_sha1_of_local_file(self, local_path):
        cmd_text = "sha1sum {} | awk '{{print $1}}'".format(local_path)
        sha1 = self.__cmd_with_output(cmd_text).decode("utf-8").strip()
        return sha1

    def __axel_cmd(self, download_url, local_file, user, password):
        args = ""

        if user and password:
            args += " \"Authorization: Basic $(echo -n '{}:{}'|base64)\"".format(user, password)
        args += " -o {}".format(local_file)
        args += " {download_url}".format(download_url=download_url)

        if os.getenv("JENKINS_URL") is not None:
            print("Initializing download: " + download_url)
            cmd_txt = "axel -q -n 8 -H  " + args
        else:
            cmd_txt = "axel -a -n 8 -H  " + args
        # print(txt)

        if not os.path.exists(os.path.join(local_file, '.st')) and os.path.exists(local_file):
            os.remove(local_file)
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        self.__cmd(cmd_txt)

    @staticmethod
    def __cmd_exists(cmd_txt):
        return subprocess.call("type " + cmd_txt, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    @staticmethod
    def __cmd_with_output(cmd_text):
        ret = subprocess.run(cmd_text, stdout=subprocess.PIPE, shell=True)
        return ret.stdout

    @staticmethod
    def __cmd(cmd_text, ignore_error=False):
        # print("RUN_CMD: " + cmd_text)
        ret = subprocess.call(cmd_text, shell=True)
        if ret != 0 and not ignore_error:
            print("Error on cmd : '%s'" % cmd_text)
            print("return code = %d" % ret)
            exit(-1)
        else:
            return ret


class Artifact(object):
    def __init__(self, item_cfg: dict, version: str):
        self.name = item_cfg.get('name')  # type: str
        self.path_in_repo = item_cfg.get('path_in_repo')  # type: str
        # expand version
        self.path_in_repo = self.path_in_repo.replace("${version}", version)

        self.filename = self.path_in_repo
        # initialize later
        self.local_file = ""

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class Config(object):
    def __init__(self, config_file: str, download_dir: str):
        self.name = ''
        self.version = ''
        self.artifacts = []  # type: List[Artifact]

        self.__load_config(config_file, download_dir)

    def __load_config(self, artifact_config_file, download_dir):
        cfg_filename = os.path.abspath(artifact_config_file)
        local_root_dir = os.path.abspath(download_dir)
        if not resolve_only:
            print("Try loading config file: " + cfg_filename)
        with open(str(cfg_filename)) as f:
            content = f.read()
            try:
                cfg = yaml.load(content)
            except Exception as e:
                # print(e)
                cfg = yaml.load(content,Loader=yaml.FullLoader)
            self.name = cfg["name"]
            self.version = cfg['version']
            for artifact_cfg in cfg['artifacts']:
                artifact = Artifact(artifact_cfg, self.version)
                artifact.local_file = os.path.join(local_root_dir, artifact.filename)
                self.artifacts.append(artifact)

    def __str__(self):
        return str(self.__dict__)


def download(config: Config):
    helper = DownloadHelper()
    total = len(config.artifacts)
    for index, artifact in enumerate(config.artifacts):
        progress = "({}/{})".format(index + 1, total)
        if artifact.path_in_repo.endswith(".zip") or artifact.path_in_repo.endswith("tar.gz"):
            helper.download(artifact.path_in_repo, artifact.local_file, progress)


def print_artifacts(config: Config):
    for artifact in config.artifacts:
        print(artifact.path_in_repo)


def parse_args():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    config = Config(os.path.join(script_path, "config.yml"), script_path)
    # print(config)
    if parse_args() == "resolve":
        # Resolve only
        print_artifacts(config)
    else:
        download(config)


if __name__ == '__main__':
    resolve_only = False
    if parse_args() == "resolve":
        resolve_only = True
    if not resolve_only:
        print("Working dir    : " + os.getcwd())
        print("Python         : " + sys.executable)
        print("Python version : " + re.sub(r'\n', '', sys.version))
        print()
    main()
