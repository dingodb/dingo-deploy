#!/usr/bin/env python
import json


class FilterModule(object):
    def filters(self):
        return {
            'cidr': self.cidr,
            'json_result': self.json_result,
        }

    @staticmethod
    def cidr(ip, netmask):
        return ip + "/" + str(sum(bin(int(x)).count('1') for x in netmask.split('.')))

    @staticmethod
    def json_result(json_str):
        json_result = {}
        try:
            json_result = json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return json_result
