import sys
from functools import wraps

import click
from click.globals import get_current_context
from terminaltables import SingleTable

from .bridgeconfig import BridgeConfig


def print_table(headers, rows, empty_table_msg="No values found"):
    rows = list(rows) if not isinstance(rows, list) else rows  # allow generators

    if not rows:
        print(empty_table_msg)  # noqa
        return

    print(SingleTable([headers] + rows).table)  # noqa


def pass_bridgeconfig(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(get_current_context().obj["bridgeconfig"], *args, **kwargs)

    return wrapper


@click.group()
@click.option(
    "-p",
    "--project",
    default=None,
    help="project name (default: search for settings.toml",
)
@click.option(
    "-e",
    "--environment",
    default="dev",
    type=click.Choice(
        ("dev", "develop", "stg", "staging", "prod", "production", "All"),
        case_sensitive=False,
    ),
    envvar="ENVIRONMENT",
    help="environment name",
)
@click.pass_context
def cli(ctx, project, environment):
    if ctx.invoked_subcommand != "version":
        if project is None:
            from .conf import get_app_name

            project = get_app_name()

        bc = BridgeConfig(project, environment)
    else:
        bc = None

    ctx.ensure_object(dict)
    ctx.obj.update({"project": project, "environment": environment, "bridgeconfig": bc})


@cli.command()
def version():
    from . import VERSION

    print("bridgeconfig: v{}".format(VERSION))  # noqa
    sys.exit(0)


@cli.command(name="show", help="list all or selected parameters")
@click.argument("keys", nargs=-1)
@click.option("-x", "--decrypt", help="decrypt parameters on listing", is_flag=True)
@pass_bridgeconfig
def show_paramters(bc, keys, decrypt):
    print_table(
        ("Path", "Value"),
        (
            (
                parameter["name"],
                "<ENCRYPTED>"
                if not decrypt and bc.is_encrypted(parameter["name"])
                else parameter["value"],
            )
            for parameter in bc.get_all_parameters(decrypt=decrypt)
            if not len(keys) or bc.get_param_name(parameter["name"]) in keys
        ),
    )


@cli.command(name="history", help="get history of a parameter")
@click.argument("key")
@click.option("-x", "--decrypt", help="decrypt parameters on listing", is_flag=True)
@pass_bridgeconfig
def show_paramter_history(bc, key, decrypt):
    print_table(
        ("Revision ID", "Value", "Modifier", "Last Modified"),
        (
            (
                item["Version"],
                "<ENCRYPTED>" if not decrypt else item["Value"],
                item["LastModifiedUser"],
                item["LastModifiedDate"],
            )
            for item in bc.get_parameter_history(path=key, decrypt=decrypt)
        ),
    )


@cli.command(name="set", help="add or modify an existing parameter")
@click.option(
    "-t",
    "--type",
    default="String",
    type=click.Choice(("String", "SecureString"), case_sensitive=False),
    help="parameter type",
)
@click.argument("key")
@click.argument("value")
@pass_bridgeconfig
def set_parameter(bc, type, key, value):
    bc.set_parameter(key, value, type)


@cli.command(name="delete", help="delete a parameter")
@click.argument("key")
@pass_bridgeconfig
def delete_parameter(bc, key):
    bc.delete_paramter(key)


@cli.command(name="list", help="list available projects")
@pass_bridgeconfig
def list_projects(bc):
    print_table(
        ("Project Name",),
        (
            (pjt,)
            for pjt in bc.get_parameter(path="/bridgeconfig/All/Projects", type="csv")
        ),
    )
