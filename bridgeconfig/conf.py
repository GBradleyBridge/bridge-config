import os
from os.path import dirname, exists, join

import toml
from dynaconf import LazySettings
from dynaconf.utils.parse_conf import LazyFormat, converters

from .bridgeconfig import BridgeConfig


def guess_settings_path(envvar="SETTINGS_PATH", allow_cwd=True):
    path = os.environ.get(envvar)
    if path and exists(join(path, "settings.toml")):
        return path
    if path and exists(join(path, "etc/settings.toml")):
        return join(path, "etc")

    if allow_cwd:
        path = os.getcwd()
        while path and path != "/":
            if exists(join(path, "etc/settings.toml")):
                return join(path, "etc")
            if exists(join(path, "settings.toml")):
                return path
            path = dirname(path)

    raise Exception("unable to guess settings.toml location")


def get_app_name(settings_path=None, envvar="APP_NAME"):
    app_name = os.environ.get(envvar)
    if not app_name:
        if settings_path is None:
            settings_path = guess_settings_path()

        with open(join(settings_path, "settings.toml")) as fp:
            app_name = toml.load(fp).get("default", {}).get("APP_NAME")

    if not app_name:
        raise Exception("unable to idetify the app name")

    return app_name


class Settings(LazySettings):
    def _setup(self):
        for k, v in self._kwargs.items():
            if callable(v):
                self._kwargs[k] = v()
        super()._setup()


class AWSFormatter(object):
    token = "aws"

    def __init__(self, bridge_config=None):
        self.bridge_config = None

    def split_options(self, value):
        value = value.split(" ", 1)
        path = value[0]
        options = value[-1].split(",") if len(value) > 1 else []
        return path, options

    def __call__(self, value, **context):
        settings = context["this"]

        if self.bridge_config is None:
            self.bridge_config = BridgeConfig(settings.APP_NAME, settings.current_env)

        path, options = self.split_options(value)

        decrypt = False
        if "decrypt" in options:
            options.remove("decrypt")
            decrypt = True

        if len(options) > 1:
            raise ValueError("invalid options provided [{}]".format(options))
        elif options:
            cast_type = options[0]
        else:
            cast_type = "string"

        return self.bridge_config.get_parameter(path, type=cast_type, decrypt=decrypt)


aws_formatter = AWSFormatter()


converters[f"@{aws_formatter.token}"] = lambda value: LazyFormat(
    value, formatter=aws_formatter
)


settings = Settings(
    ENVIRONMENTS_FOR_DYNACONF=True,
    PRELOAD_FOR_DYNACONF="static_settings.py",
    DEBUG_LEVEL_FOR_DYNACONF="DEBUG",
    ENV_SWITCHER_FOR_DYNACONF="ENVIRONMENT",
    ROOT_PATH_FOR_DYNACONF=guess_settings_path,
    SETTINGS_FILE_FOR_DYNACONF=["settings.toml"],
)
