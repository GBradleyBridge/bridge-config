from __future__ import print_function
import os
import boto3
import logging
import json
import configparser


class LocalEnvironmentFileDoesNotExists(Exception):
    pass


class BridgeConfig(object):

    def __init__(self, project, environment):
        self.project = project
        self.environment = environment
        self.local_env_file = ".local.env"
        if os.path.exists(".local.env"):
            self.environment = "local"
            logging.warning("using local environment variables")
        else:
            self.client = boto3.client('ssm', region_name="us-east-1")

    def get_local_env_from_file(self):
        config = configparser.ConfigParser()
        config.read(self.local_env_file)

        return config

    def get_full_path(self, path):
        return "/{}/{}/{}".format(self.project, self.environment, path)

    def get_parameter(self, path, type="string", decrypt=True, default=None):
        fullpath = self.get_full_path(path)
        logging.debug('getting parameter: {}'.format(fullpath))

        if self.environment == "local":
            return self.get_local_parameter(path, type)
        else:
            return self.get_remote_parameter(fullpath, type, decrypt, default)

    def get_local_parameter(self, path, type):
        config = self.get_local_env_from_file()
        return self.__cast_value(config['local'][path], type)

    def get_remote_parameter(self, fullpath, type="string", decrypt=True, default=None):
        try:
            value = self.client.get_parameter(
                Name=fullpath, WithDecryption=decrypt
            )['Parameter']['Value']
            logging.debug('raw value: {}'.format(value))
        except self.client.exceptions.ParameterNotFound as e:
            logging.error('requested key {} not found'.format(fullpath))
            return default

        return self.__cast_value(value, type)

    def __cast_value(self, value, type):
        if type == "boolean":
            return bool(value)
        elif type == "integer":
            return int(value)
        elif type == "json":
            return json.loads(value)
        elif type == "float":
            return float(value)
        elif type == "code":
            return eval(value)
        else:
            return value

    def get_all_parameters(self, decrypt=False, count=10):
        if self.environment == "local":
            logging.warning(
                "get_all_parameters:running in local environment, check .local.env"
            )
            return None

        path = "/{}/{}/".format(self.project, self.environment)
        result = list()
        finish = 0
        second_round = 0
        raw_paramters = dict()

        while finish == 0:
            if 'NextToken' in raw_paramters.keys():
                raw_paramters = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=decrypt,
                    NextToken=raw_paramters['NextToken']
                )
            else:
                raw_paramters = self.client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=decrypt,
                )

            for x in raw_paramters['Parameters']:
                result.append(
                    {'name': x['Name'], 'value': x['Value']}
                )

            if 'NextToken' not in raw_paramters.keys():
                finish = 1

        return result

    def set_parameter(self, path, value, type="String"):
        if self.environment == "local":
            logging.warning("set_parameter is disabled running in local environment")
            return None

        fullpath = self.get_full_path(path)
        return self.client.put_parameter(Name=fullpath, Value=value, Type=type,
                                         Overwrite=True)

    def delete_paramter(self, path):
        if self.environment == "local":
            logging.warning("delete_parameter is disabled running in local environment")
            return None
        fullpath = self.get_full_path(path)
        try:
            return self.client.delete_parameter(Name=fullpath)
        except self.client.exceptions.ParameterNotFound as e:
            logging.warning('requested key {} not found'.format(fullpath))
            return None


if __name__ == "__main__":
    BC = BridgeConfig('test', 'develop')
    # print BC.get_parameter('debug', 'boolean')
    # print BC.get_parameter('json', 'json')
    # print BC.get_parameter('json2', 'code')
    # print BC.get_parameter('json3', 'code')
    # print BC.get_parameter('db_user', 'string')
    # print BC.get_parameter(path='db_password', type='string', decrypt=False)
    # print BC.get_parameter('no_existe', 'string')
    # print BC.get_parameter('key1/subkey1', 'string')
    # print BC.get_all_parameters()
    # for x in BC.get_all_parameters():
    #     print x
    # print BC.get_all_parameters(decrypt=True)
    # BC.set_parameter('new_param', '123abc456', 'String')
    # print BC.delete_paramter('123abc456')
