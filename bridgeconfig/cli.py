import logging
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


def complete_registered_projects(ctx, args, incomplete):
    bc = BridgeConfig("bridgeconfig", "All")
    return [
        pjt
        for pjt in sorted(
            set(bc.get_parameter(path="Projects", type="csv")) | {"All"},
            key=lambda v: v.lower(),
        )
        if incomplete in pjt
    ]


@click.group()
@click.option(
    "--verbose",
    is_flag=True,
    help="show debugging info",
    autocompletion=complete_registered_projects,
)
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
def cli(ctx, verbose, project, environment):
    if verbose:
        logging.basicConfig()
        logging.getLogger("bridgeconfig").setLevel(logging.DEBUG)

    if ctx.invoked_subcommand != "version":
        if ctx.invoked_subcommand != "list" and project is None:
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
    if not keys:
        parameters = [
            (p["name"], p["value"]) for p in bc.get_all_parameters(decrypt=decrypt)
        ]
    else:
        parameters = [
            bc.get_parameter(key, decrypt=decrypt, include_path=True) for key in keys
        ]

    print_table(
        ("Path", "Value"),
        (
            (
                name,
                "<ENCRYPTED>" if not decrypt and bc.is_encrypted(name) else value,
            )
            for name, value in parameters
            if name
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
