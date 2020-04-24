from __future__ import print_function

import os
import logging
import json
import boto3


class BridgeConfig(object):

    def __init__(self, project, environment=None, local_environ_location='local-envs/', local_environs=('local', 'build', 'testing')):
        self.project = project
        self.environment = environment or os.environ.get('ENVIRONMENT', 'local')
        self.local_environ_location = local_environ_location
        self.local_environs = [env.lower() for env in local_environs if env]
        self._is_local_env = environment.lower() in self.local_environs
        if self._is_local_env:
            self.local_filepath = os.path.join(self.local_environ_location, self.environment.lower() + '.json')
            self._load_local_config()
        else:
            self.client = None if self._is_local_env else boto3.client('ssm', region_name="us-east-1")

    def _load_local_config(self):
        if os.path.exists(self.local_filepath):
            with open(self.local_filepath) as fp:
                self.local_config = json.load(fp)
            assert isinstance(self.local_config, dict)
        else:
            self.local_config = {}

    def get_full_path(self, path):
        return "/{}/{}/{}".format(self.project, self.environment, path)

    def get_aws_parameter(self, path, type="string", decrypt=True, default=None):
        fullpath = self.get_full_path(path)
        logging.debug('getting parameter: {}'.format(fullpath))
        try:
            value = self.client.get_parameter(
                Name=fullpath, WithDecryption=decrypt,
            )['Parameter']['Value']
            logging.debug('raw value: {}'.format(value))
        except self.client.exceptions.ParameterNotFound:
            logging.error('requested key {} not found'.format(fullpath))
            return default

    def get_parameter(self, path, tp="string", decrypt=True, default=None):
        if self._is_local_env:
            value = self.local_config.get(path, default)
        else:
            value = self.get_aws_parameter(path, tp, decrypt, default)

        return {
            "string": str,
            "boolean": bool,
            "integer": int,
            "float": float,
            "json": json.loads,
            "code": eval,
        }.get(tp, lambda v: v)(value)

    def get_string(self, path, decrypt=True, default=None):
        return self.get_parameter(path, "string", decrypt, default)

    def get_int(self, path, decrypt=True, default=None):
        return self.get_parameter(path, "integer", decrypt, default)

    def get_float(self, path, decrypt=True, default=None):
        return self.get_parameter(path, "float", decrypt, default)

    def get_json(self, path, decrypt=True, default=None):
        return self.get_parameter(path, "json", decrypt, default)

    def get_code(self, path, decrypt=True, default=None):
        return self.get_parameter(path, "code", decrypt, default)

    def get(self, path, decrypt=True, default=None):
        return self.get_parameter(path, None, decrypt, default)

    def get_all_aws_parameters(self, decrypt=False, count=10):
        path = "/{}/{}/".format(self.project, self.environment)
        result = []
        finish = 0
        raw_paramters = {}

        while finish == 0:
            if 'NextToken' in raw_paramters.keys():
                raw_paramters = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=decrypt,
                    NextToken=raw_paramters['NextToken'],
                )
            else:
                raw_paramters = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=decrypt,
                )

            for x in raw_paramters['Parameters']:
                result.append(
                    {'name': x['Name'], 'value': x['Value']},
                )

            if 'NextToken' not in raw_paramters.keys():
                finish = 1

        return result

    def set_aws_parameter(self, path, value, type="String"):
        fullpath = self.get_full_path(path)
        return self.client.put_parameter(Name=fullpath, Value=value, Type=type,
                                         Overwrite=True)

    def delete_aws_parameter(self, path):
        fullpath = self.get_full_path(path)
        try:
            return self.client.delete_parameter(Name=fullpath)
        except self.client.exceptions.ParameterNotFound:
            logging.warning('requested key {} not found'.format(fullpath))
            return None

    def select_param(self, **environs):
        return environs.get(
            self.environment.lower(),           # try environ as lower case
            environs.get(
                self.environment.upper(),       # try as upper case
                environs.get('default', None),  # if default keyword was provided use that, otherwise return None
            ),
        )


if __name__ == "__main__":
    BC = BridgeConfig('test', 'develop')
    # print(BC.get_parameter('debug', 'boolean'))
    # print(BC.get_parameter('json', 'json'))
    # print(BC.get_parameter('json2', 'code'))
    # print(BC.get_parameter('json3', 'code'))
    # print(BC.get_parameter('db_user', 'string'))
    # print(BC.get_parameter(path='db_password', type='string', decrypt=False))
    # print(BC.get_parameter('no_existe', 'string'))
    # print(BC.get_parameter('key1/subkey1', 'string'))
    # print(BC.get_all_aws_parameters())
    # for x in BC.get_all_aws_parameters():
    #     print(x)
    # print(BC.get_all_aws_parameters(decrypt=True))
    # BC.set_aws_parameter('new_param', '123abc456', 'String')
    # print(BC.delete_aws_parameter('123abc456'))
