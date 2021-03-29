Bridge Marketing config
=======================

Add the following line to your project's requirement.txt file and replace
with the desired version

```
-e git+https@github.com:BridgeMarketing/bridge-config.git@v1.3#egg=bridge_config
```


Usage:

In your settings.py:

```python
from bridgeconfig import bridgeconfig

# if no project is specified it will search for settings.toml or etc/settings.toml
# descending on parent directories if it is found [default]APP_NAME will be used as project
# if environment is not specified it will default to dev
bc = bridgeconfig.BridgeConfig(project="<project_name>", environment="<environment>")


DEBUG = bc.get_parameter(path="debug", type="boolean") # Cast to boolean
SUBITEM = bc.get_parameter(path="subitem", type=bool) # callable is also accepted
SOME_CONFIG = bc.get_parameter(path="config", type=msgpack.unpackb) # callable is also accepted

KEY = bc.get_parameter(path="/Other/Test/KEY", type=bool) # we can specify the full path (/<project>/<environment>/<key>)
KEY = bc.get_parameter(path="Test/KEY", type=bool) # or just the environment (<environment>/<key>)

DB_USER = bc.get_parameter('db_user', 'string') # Cast to string (default)
NON_EXISTENT = bc.get_parameter('non_existent', 'string') # This item doesn't exists so
                                                          # None will be stored in SUBITEM
DB_PASSWORD =  bc.get_parameter(path='db_password', type='string',
                            decrypt=True) # The DECRYPTED version of db_password will be saved
JAJA_CONFIG = {"as": "b", "cd": "dd"} # For educative intentions
JSON_VALUE = bc.get_parameter(path='weird_config', type='json')

# probably code will go since it is a security issue
LIST = bc.get_parameter(path='list_of_things', type='code')
DICT = bc.get_parameter(path='python_dict', type='code')
```

Check if a parameter is encrypted or not:

```python
if bc.is_encrypted(path='db_password'):
    print("it is encrypted")
else:
    print("it isn't encrypted")
```


The path of the parameters should be:

**/project/environment/key1**

If a subkey is requried fullpath (**/project/environment/subkey1/subkey2/.../subkeyN**) must be passed to all methods


# Bridge Config Tool (cli)

This a cli tool to help to manage the data for the bridgeconfig library.

## BridgeConfig (bridgeconfig)

```
$ bridgeconfig --help
Usage: bridgeconfig [OPTIONS] COMMAND [ARGS]...

Options:
  -p, --project TEXT              project name (default: search for
                                  settings.toml

  -e, --environment [dev|develop|stg|staging|prod|production|All]
                                  environment name
  --help                          Show this message and exit.

Commands:
  delete   delete a parameter
  history  get history of a parameter
  list     list available projects
  set      add or modify an existing parameter
  show     list all or selected parameters
  version
```

## Enable Autocomplete

For Bash, add this to ~/.bashrc:

```
eval "$(_FOO_BAR_COMPLETE=source_bash foo-bar)"
```

For Zsh, add this to ~/.zshrc:

```
eval "$(_FOO_BAR_COMPLETE=source_zsh foo-bar)"
```

For Fish, add this to ~/.config/fish/completions/foo-bar.fish:

```
eval (env _FOO_BAR_COMPLETE=source_fish foo-bar)
```

### [-p PROJECT]

Specify the project, it can also search for the APP_NAME in the settings.toml so if the command is ran inside a repository it will select that project by default.

Autocomplete is enabled if the users has access to /bridgeconfig/All/Projects parameter.

### [-e ENVIRONMENT]

Specifies the environment to user (options are dev|develop|stg|staging|prod|production|All) it can pick the value from the ENVIRONMETN variable or it will default to dev.


## Commands

### show [-x]

Will show all the configured parameters for a given project in a given environment.

Example:

```
$ bridgeconfig -p wf-proxy -e develop show
NOTE: with decryption off, values are truncated to 50 chars
┌──────────────────────────────────────────────────┬────────────────────────────────────────────────────┐
│ Path                                             │ Value                                              │
├──────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ /wf-proxy/develop/cm_event_task_start_url        │ http://10.10.156.13/cm/v1/event/task/start         │
│ /wf-proxy/develop/cors_support_enabled           │ True                                               │
│ /wf-proxy/develop/debug                          │ True                                               │
│ /wf-proxy/develop/project_transitions            │ {    'TaskType1': {        'TASK_CMP':'PROJ_PLN'   │
│ /wf-proxy/develop/server_name                    │ 127.0.0.1:4500                                     │
│ /wf-proxy/develop/sqlalchemy_track_modifications │ False                                              │
│ /wf-proxy/develop/version_prefix                 │ /wp/v1                                             │
│ /wf-proxy/develop/workfront_automatic_user_id    │ AQICAHjrgw+mYxh8V1QafBX6PnTE38zIn6b91cPlXPNxlwfoKg │
│ /wf-proxy/develop/workfront_enable_auto          │ True                                               │
│ /wf-proxy/develop/workfront_user                 │ notifications@wf.bridgemarketing.com               │
│ /wf-proxy/develop/ccm_event_task_start_url       │ http://10.10.155.10:8081/workfront/routerTask      │
│ /wf-proxy/develop/check_portfolio                │ True                                               │
│ /wf-proxy/develop/develop_portfolio_ids          │ ['5b45ff9b000aa3a5db15b2e269976a4c', '5b742f970015 │
│ /wf-proxy/develop/dm_event_task_start_url        │ http://10.10.155.16/dm/v2/datacleanup/start        │
│ /wf-proxy/develop/sentry_dsn                     │ AQICAHjrgw+mYxh8V1QafBX6PnTE38zIn6b91cPlXPNxlwfoKg │
│ /wf-proxy/develop/sentry_ignore                  │ ['NotFound', 'MethodNotAllowed', 'BdbQuit', 'BadRe │
│ /wf-proxy/develop/sqlalchemy_database_uri        │ AQICAHjrgw+mYxh8V1QafBX6PnTE38zIn6b91cPlXPNxlwfoKg │
│ /wf-proxy/develop/sqlalchemy_echo                │ True                                               │
│ /wf-proxy/develop/version                        │ 1.0.0                                              │
│ /wf-proxy/develop/workfront_domain               │ thebridgecorp.sb01.workfront.com                   │
│ /wf-proxy/develop/testing                        │ True                                               │
│ /wf-proxy/develop/workfront_pass                 │ AQICAHjrgw+mYxh8V1QafBX6PnTE38zIn6b91cPlXPNxlwfoKg │
└──────────────────────────────────────────────────┴────────────────────────────────────────────────────┘
```

It's possible to show the actual values of encrypted values by adding -x

```
$ bridgeconfig -p wf-proxy -e develop show -x
┌──────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Path                                             │ Value                                                                                                   │
├──────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ /wf-proxy/develop/cm_event_task_start_url        │ http://10.10.156.13/cm/v1/event/task/start                                                              │
│ /wf-proxy/develop/cors_support_enabled           │ True                                                                                                    │
│ /wf-proxy/develop/debug                          │ True                                                                                                    │
│ /wf-proxy/develop/project_transitions            │ {                                                                                                       │
│                                                  │     'TaskType1': {                                                                                      │
│                                                  │         'TASK_CMP':'PROJ_PLN',                                                                          │
│                                                  │         'TASK_INP':'PROJ_BLA',                                                                          │
│                                                  │     },                                                                                                  │
│                                                  │     'TaskType2': {                                                                                      │
│                                                  │         'TASK_CMP':'PROJ_PLN',                                                                          │
│                                                  │         'TASK_INP':'PROJ_BLA',                                                                          │
│                                                  │     },                                                                                                  │
│                                                  │ }                                                                                                       │
│ /wf-proxy/develop/server_name                    │ 127.0.0.1:4500                                                                                          │
│ /wf-proxy/develop/sqlalchemy_track_modifications │ False                                                                                                   │
│ /wf-proxy/develop/version_prefix                 │ /wp/v1                                                                                                  │
│ /wf-proxy/develop/workfront_automatic_user_id    │ 5a394076002d8b247f9448078226c445                                                                        │
│ /wf-proxy/develop/workfront_enable_auto          │ True                                                                                                    │
│ /wf-proxy/develop/workfront_user                 │ notifications@wf.bridgemarketing.com                                                                    │
│ /wf-proxy/develop/ccm_event_task_start_url       │ http://10.10.155.10:8081/workfront/routerTask                                                           │
│ /wf-proxy/develop/check_portfolio                │ True                                                                                                    │
│ /wf-proxy/develop/develop_portfolio_ids          │ ['5b45ff9b000aa3a5db15b2e269976a4c', '5b742f970015be8cb92789cb63b15619']                                │
│ /wf-proxy/develop/dm_event_task_start_url        │ http://10.10.155.16/dm/v2/datacleanup/start                                                             │
│ /wf-proxy/develop/sentry_dsn                     │ https://f5fc521f2c2a45ea8932d188c36465f6:c6af16a5e9484c0497f00986b434d6cf@sentry.io/280888              │
│ /wf-proxy/develop/sentry_ignore                  │ ['NotFound', 'MethodNotAllowed', 'BdbQuit', 'BadRequest']                                               │
│ /wf-proxy/develop/sqlalchemy_database_uri        │ mysql://bridge:kakarulo1987@dpfeaezpj278j1.cixjbteelrgv.us-east-1.rds.amazonaws.com/b20_wp?charset=utf8 │
│ /wf-proxy/develop/sqlalchemy_echo                │ True                                                                                                    │
│ /wf-proxy/develop/version                        │ 1.0.0                                                                                                   │
│ /wf-proxy/develop/workfront_domain               │ thebridgecorp.sb01.workfront.com                                                                        │
│ /wf-proxy/develop/testing                        │ True                                                                                                    │
│ /wf-proxy/develop/workfront_pass                 │ beef6060                                                                                                │
└──────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```


### set [-t String|SecureString] <key> <value>

This will add/update a key with specified value and type to a given project in a given environment.

```
$ bridgeconfig -p wf-proxy -e develop set "a_key" "a_value" -t String
```

### delete <key>

This will attempt to delete a parameter for the given project and environment.


### list

This will list the registered projects (requires access to read /bridgeconfig/All/Projects parameter)
