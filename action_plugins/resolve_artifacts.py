#!/usr/bin/env python

import os
import yaml
from ansible.plugins.action import ActionBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()


class ActionModule(ActionBase):
    """ Returns map of inventory hosts and their associated SCM hostIds """

    def run(self, tmp=None, task_vars=None):
        script_path = os.path.dirname(os.path.realpath(__file__))
        artifact_path = os.path.realpath(os.path.join(script_path, "../artifacts"))
        config_file = os.path.realpath(os.path.join(artifact_path, "config.yml"))
        display.display("Loading configs from '%s'" % config_file)

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        try:
            cfg = yaml.safe_load(open(config_file).read())
            version = cfg['version']
            artifacts = {c['name']: self.process_artifact(artifact_path, c, version) for c in cfg['artifacts']}
        except KeyError as e:
            result['failed'] = True
            result['msg'] = str(e)
            return result

        result['ansible_facts'] = artifacts
        return result

    @staticmethod
    def process_artifact(artifact_path, artifact_info, version):
        # print(comp)
        artifact_info['path_in_repo'] = artifact_info['path_in_repo'].replace("${version}", version)
        local_file_name = os.path.join(artifact_path, artifact_info['path_in_repo'])
        display.display("Huzx==> Load path_in_repo '%s'" % artifact_info['path_in_repo'])
        return local_file_name
