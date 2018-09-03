import boto3
import logging


class BridgeConfig(object):

    def __init__(self, project, environment):
        self.project = project
        self.environment = environment
        self.client = boto3.client('ssm')

    def get_parameter(self, path, type="string", decrypt=False):
        fullpath = "/{}/{}/{}".format(self.project, self.environment, path)
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


if __name__ == "__main__":
    BC = BridgeConfig('test', 'develop')
    print BC.get_parameter('debug', 'boolean')
    print BC.get_parameter('db_user', 'string')
    print BC.get_parameter(path='db_password', type='string', decrypt=False)
    print BC.get_parameter('no_existe', 'string')
    print BC.get_parameter('key1/subkey1', 'string')
