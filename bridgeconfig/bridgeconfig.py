import boto3
import logging


class BridgeConfig(object):

    def __init__(self, project, environment):
        self.project = project
        self.environment = environment
        self.client = boto3.client('ssm')

    def __get_full_path(self, path):
        return "/{}/{}/{}".format(self.project, self.environment, path)

    def get_parameter(self, path, type="string", decrypt=False):
        fullpath = self.__get_full_path(path)
        logging.debug('getting parameter: {}'.format(fullpath))
        try:
            value = self.client.get_parameter(
                Name=fullpath, WithDecryption=decrypt
            )['Parameter']['Value']
            logging.debug('raw value: {}'.format(value))
        except self.client.exceptions.ParameterNotFound, e:
            logging.warning('requested key {} not found'.format(fullpath))
            return None

        if type == "boolean":
            return bool(value)
        elif type == "integer":
            return int(value)
        else:
            return value

    def get_all_parameters(self, decrypt=False, count=10):
        path = "/{}/{}/".format(self.project, self.environment)
        raw_paramters = self.client.get_parameters_by_path(
            Path=path,
            Recursive=True,
            WithDecryption=decrypt,
            MaxResult=count
        )
        return [
            {'name': x['Name'], 'value': x['Value']}
            for x in raw_paramters['Parameters']
        ]

    def set_parameter(self, path, value, type="String"):
        fullpath = self.__get_full_path(path)
        return self.client.put_parameter(Name=fullpath, Value=value, Type=type,
                                         Overwrite=True)

    def delete_paramter(self, path):
        fullpath = self.__get_full_path(path)
        try:
            return self.client.delete_parameter(Name=fullpath)
        except self.client.exceptions.ParameterNotFound, e:
            logging.warning('requested key {} not found'.format(fullpath))
            return None


if __name__ == "__main__":
    BC = BridgeConfig('test', 'develop')
    print BC.get_parameter('debug', 'boolean')
    print BC.get_parameter('db_user', 'string')
    print BC.get_parameter(path='db_password', type='string', decrypt=False)
    print BC.get_parameter('no_existe', 'string')
    print BC.get_parameter('key1/subkey1', 'string')
    print BC.get_all_parameters()
    print BC.get_all_parameters(decrypt=True)
    BC.set_parameter('new_param', '123abc456', 'String')
    print BC.delete_paramter('123abc456')
