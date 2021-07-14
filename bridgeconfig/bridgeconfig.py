import json
import logging
import pickle
from os.path import join

import boto3

EMPTY = object()


def to_bool(value):
    return not (
        not value or value in ("no", "NO", "No", "0", "false", "False", "FALSE")
    )


class ParameterNotFound(Exception):
    def __init__(self, key, search_path):
        self.key = key
        self.search_path = search_path
        super().__init__("Parameter {} not found in {}".format(key, search_path))


DEFAULT_CONVERSIONS = {
    "boolean": to_bool,
    "bool": to_bool,
    "integer": int,
    "int": int,
    "long": int,
    "json": json.loads,
    "dict": json.loads,
    "pickle": pickle.loads,
    "float": float,
    "code": eval,  # Should we keep this one since is a security issue?
    "list": lambda value: [v.strip() for v in value.split(",") if v.strip()],
    "csv": lambda value: [v.strip() for v in value.split(",") if v.strip()],
    "": lambda value: value,
    None: lambda value: value,
}

log = logging.getLogger("bridgeconfig")


def list_chunks(lst, chunk_size):
    for index in range(0, len(lst), chunk_size):
        yield lst[index: index + chunk_size]


class BridgeConfig(object):
    def __init__(self, project, environment, value=None, store_type="String"):
        self.project = project
        self.environment = environment
        self.client = boto3.client("ssm", region_name="us-east-1")

    def get_param_name(self, path):
        return path.lstrip("/").split("/", 2)[-1]

    def refresh_cache(self):
        log.debug("refreshing cache")
        self._cache = self.get_raw_parameters()
        self._lookup = {parm["Name"]: parm for parm in self._cache}
        self._names = {self.get_param_name(path): path for path in self._lookup}

    @property
    def cache(self):
        if not hasattr(self, "_cache"):
            self.refresh_cache()
        return self._cache

    @property
    def lookup(self):
        if not hasattr(self, "_lookup"):
            self.refresh_cache()
        return self._lookup

    @property
    def names(self):
        if not hasattr(self, "_names"):
            self.refresh_cache()
        return self._names

    @property
    def still_encrypted(self):
        return {
            name: path
            for name, path in self.names.items()
            if self.lookup[path]["Type"] == "SecureString"
            and not self.lookup[path].get("Decrypted")
        }

    @property
    def project_search_path(self):
        return ("All", self.project) if self.project != "All" else ("All",)

    @property
    def environment_search_path(self):
        return ("All", self.environment) if self.environment != "All" else ("All",)

    @property
    def search_path(self):
        return [
            "/{}/{}/".format(pjt, env)
            for pjt in self.project_search_path
            for env in self.environment_search_path
        ]

    def get_raw_parameters(self, decrypt=False):
        result = []

        for path in self.search_path:
            raw_paramters = {}

            while True:
                payload = {
                    "Path": path,
                    "Recursive": True,
                    "WithDecryption": decrypt,
                }

                if "NextToken" in raw_paramters:
                    payload["NextToken"] = raw_paramters["NextToken"]

                raw_paramters = self.client.get_parameters_by_path(**payload)

                for x in raw_paramters["Parameters"]:
                    result.append(x)

                if "NextToken" not in raw_paramters:
                    break

        return result

    def is_encrypted(self, path, default=None):
        if path in self.names:
            path = self.names[path]
        return self.lookup[path]["Type"] == "SecureString"

    def decrypt_parameters(self, parameters=None):
        parameters = self.names if parameters is None else parameters
        pending_to_decrypt = [
            path
            for name, path in self.still_encrypted.items()
            if name in parameters or path in parameters
        ]
        if pending_to_decrypt:
            for params_chunk in list_chunks(pending_to_decrypt, 10):
                for param in self.client.get_parameters(
                    Names=params_chunk, WithDecryption=True
                )["Parameters"]:
                    self.lookup[param["Name"]]["Value"] = param["Value"]
                    self.lookup[param["Name"]]["Decrypted"] = True

    def get_all_parameters(self, decrypt=False, count=10, sorted=True):
        if decrypt:
            self.decrypt_parameters()
        parameters = [
            {"name": self.lookup[path]["Name"], "value": self.lookup[path]["Value"]}
            for path in self.names.values()
        ]
        if sorted:

            def sort_by_path(param):
                path = param["name"]
                project, environment, path = path.lstrip("/").split("/", 2)
                return (
                    1 if project == self.project else 2,
                    1 if environment == self.environment else 2,
                    path,
                )

            parameters.sort(key=sort_by_path)
        return parameters

    def get_full_path(self, path):
        parts = path.lstrip("/").split("/", 2)
        if len(parts) == 3:
            project, environment, path = parts
        elif len(parts) == 2:
            project = self.project
            environment, path = parts
        else:
            project, environment = self.project, self.environment
        return "/{}/{}/{}".format(project, environment, path)

    def parameter_sarch_path(self, path):
        parts = path.lstrip("/").split("/", 2)
        if len(parts) == 3:
            yield "/" + path.lstrip("/")
        elif len(parts) == 2:
            environment, path = parts
            yield from (
                "/{}/{}/{}".format(project, environment, path)
                for project in reversed(self.project_search_path)
            )
        else:
            yield from (join(base, path) for base in reversed(self.search_path))

    def get_parameter(
        self, path, type=None, decrypt=True, default=EMPTY, include_path=False
    ):
        if path in self.names:
            search_path = [self.names[path]]
        elif path in self.lookup:
            search_path = [path]
        else:
            search_path = list(self.parameter_sarch_path(path))

        log.debug(
            "getting parameter: {} with search paths {}".format(path, search_path)
        )

        for fullpath in search_path:
            if fullpath in self.lookup:
                if decrypt:
                    self.decrypt_parameters([fullpath])
                value = self.lookup[fullpath]["Value"]
                break
        else:
            for fullpath in search_path:
                try:
                    param = self.client.get_parameter(
                        Name=fullpath, WithDecryption=decrypt
                    )["Parameter"]
                    if decrypt and param["Type"] == "SecureString":
                        param["Decrypted"] = True
                    self._cache.append(param)
                    self.lookup[param["Name"]] = param
                    value = param["Value"]
                    break
                except self.client.exceptions.ParameterNotFound:
                    log.debug("parameter: {} Not Found in ssm".format(fullpath))
            else:
                if default is EMPTY:
                    raise ParameterNotFound(path, search_path)
                return (None, default) if include_path else default

        if callable(type):
            value = type(value)
        else:
            value = DEFAULT_CONVERSIONS.get(type, DEFAULT_CONVERSIONS[None])(value)
        return (fullpath, value) if include_path else value

    def set_parameter(self, path, value, type="String"):
        fullpath = self.get_full_path(path)
        return self.client.put_parameter(
            Name=fullpath, Value=value, Type=type, Overwrite=True
        )

    def delete_paramter(self, path):
        fullpath = self.get_full_path(path)
        try:
            return self.client.delete_parameter(Name=fullpath)
        except self.client.exceptions.ParameterNotFound:
            logging.warning("requested key {} not found".format(fullpath))
            return None

    def version(self):
        from . import VERSION

        return "bridgeconfig v{}".format(VERSION)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    BC = BridgeConfig('test', 'develop')
    #print(BC.get_raw_parameters(decrypt=True))
    print(BC.get_parameter_history('debug', decrypt=True))
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
