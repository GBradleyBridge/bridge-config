from __future__ import print_function
import boto3
import logging
import json


class BridgeConfig(object):

    def __init__(self, project, environment):
        self.project = project
        self.environment = environment
        self.client = boto3.client('ssm', region_name="us-east-1")
        logging.info("caching raw parameters")
        self.cache = self.get_raw_parameters()
        logging.info("raw parameters cached")

    def refresh_cache(self):
        logging.info("refreshing cache")
        self.cache = self.get_raw_parameters()

    def get_full_path(self, path):
        return "/{}/{}/{}".format(self.project, self.environment, path)

    def get_parameter(self, path, type="string", decrypt=True, default=None):
        fullpath = self.get_full_path(path)
        logging.debug('getting parameter: {}'.format(fullpath))
        try:
            value = self.client.get_parameter(
                Name=fullpath, WithDecryption=decrypt
            )['Parameter']['Value']
            logging.debug('raw value: {}'.format(value))
        except self.client.exceptions.ParameterNotFound as e:
            logging.error('requested key {} not found'.format(fullpath))
            return default

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

    def is_encrypted(self, path, default=None):
        fullpath = self.get_full_path(path)
        result = list(filter(lambda x: x['Name'] == fullpath, self.cache))[0]
        return result['Type'] == "SecureString"

    def get_raw_parameters(self, decrypt=False):
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
                    WithDecryption=decrypt
                )

            for x in raw_paramters['Parameters']:
                result.append(x)

            if 'NextToken' not in raw_paramters.keys():
                finish = 1

        return result

    def get_all_parameters(self, decrypt=False, count=10):
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
        fullpath = self.get_full_path(path)
        return self.client.put_parameter(Name=fullpath, Value=value, Type=type,
                                         Overwrite=True)

    def delete_paramter(self, path):
        fullpath = self.get_full_path(path)
        try:
            return self.client.delete_parameter(Name=fullpath)
        except self.client.exceptions.ParameterNotFound as e:
            logging.warning('requested key {} not found'.format(fullpath))
            return None

    def version(self):
        print("bridgeconfig v1.3")


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    BC = BridgeConfig('test', 'develop')
    print(BC.get_raw_parameters(decrypt=True))
    #print(BC.get_parameter('debug', 'boolean'))
    #print(BC.get_parameter('json', 'json'))
    # print BC.get_parameter('json2', 'code')
    # print BC.get_parameter('json3', 'code')
    # print BC.get_parameter('db_user', 'string')
    #print( BC.get_parameter(path='db_password', type='string', decrypt=False) )
    #print( BC.is_encrypted(path='db_password') )
    #print( BC.is_encrypted(path='db_password') )
    #print( BC.is_encrypted(path='db_password') )
    #print( BC.is_encrypted(path='db_password') )
    #print( BC.is_encrypted(path='db_password') )
    #print( BC.is_encrypted(path='db_password') )
    # print BC.get_parameter('no_existe', 'string')
    # print BC.get_parameter('key1/subkey1', 'string')
    # print BC.get_all_parameters()
    #for x in BC.get_all_parameters():
    #    print(x)
    #BC.refresh_cache()
    # print BC.get_all_parameters(decrypt=True)
    # BC.set_parameter('new_param', '123abc456', 'String')
    # print BC.delete_paramter('123abc456')
