import os
from os.path import dirname, exists, join

import toml
from dynaconf import LazySettings
from dynaconf.utils.parse_conf import LazyFormat, converters

from .bridgeconfig import BridgeConfig


def guess_settings_path(envvar="SETTINGS_PATH"):
    path = os.environ.get(envvar)
    if path and exists(join(path, "settings.toml")):
        return path
    if path and exists(join(path, "etc/settings.toml")):
        return join(path, "etc")

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


def aws_formatter(value, **context):
    value = value.split(" ", 1)
    path = value[0]
    options = value[-1].split(",") if len(value) > 1 else []

    if "decrypt" in options:
        decrypt = True
        options.remove("decrypt")
    else:
        decrypt = False

    if len(options) > 1:
        raise ValueError("invalid options provided [{}]".format(options))
    elif options:
        cast_type = options[0]
    else:
        cast_type = "string"

    return bc.get_parameter(path, type=cast_type, decrypt=decrypt)


def aws_converter(value):
    return LazyFormat(value, formatter=aws_formatter)


class Proxy(object):
    def __init__(self, on_create):
        assert callable(on_create)
        self._on_create = on_create
        self._obj = None

    def __getattr__(self, attr):
        if self._obj is None:
            self._obj = self._on_create()
        return getattr(self._obj, attr)

    def __getitem__(self, name):
        if self._obj is None:
            self._obj = self._on_create()
        return self._obj[name]


converters["@aws"] = aws_converter


settings = Proxy(
    lambda: LazySettings(
        PRELOAD_FOR_DYNACONF="static_settings.py",
        DEBUG_LEVEL_FOR_DYNACONF="DEBUG",
        ENV_SWITCHER_FOR_DYNACONF="ENVIRONMENT",
        ROOT_PATH_FOR_DYNACONF=guess_settings_path(),
    )
)

bc = Proxy(lambda: BridgeConfig(settings["APP_NAME"], settings["current_env"]))
