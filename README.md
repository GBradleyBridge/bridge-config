Bridge Marketing config
=======================

Add the following line to your project's requirement.txt file and replace v0.1
with the desired version

```
-e git+git@github.com:BridgeMarketing/bridge-config.git@v0.1#egg=bridge_config
```


Usage:

In your settings.py:

```python
from bridgeconfig import bridgeconfig

BC = bridgeconfig.BridgeConfig(project="<project_name>", environment="<environment>")

DEBUG = BC.get_parameter(path="debug", type="boolean")
SUBITEM = BC.get_parameter(path="key1/subkey1", type="boolean")
DB_USER = BC.get_parameter('db_user', 'string')
DB_PASSWORD =  BC.get_parameter(path='db_password', type='string', 
                            decrypt=True)
JAJA_CONFIG = {"as": "b", "cd": "dd"}
```

The path of the parameters should be:

**/project/environment/key/**
