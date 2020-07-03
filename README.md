Bridge Marketing config
=======================

Add the following line to your project's requirement.txt file and replace v0.1
with the desired version

```
-e git+https@github.com:BridgeMarketing/bridge-config.git@v0.0#egg=bridge_config
```


Usage:

In your settings.py:

```python
from bridgeconfig import bridgeconfig

BC = bridgeconfig.BridgeConfig(project="<project_name>", environment="<environment>")

DEBUG = BC.get_parameter(path="debug", type="boolean") # Cast to boolean
SUBITEM = BC.get_parameter(path="key1/subkey1", type="boolean") # Cast to boolean
DB_USER = BC.get_parameter('db_user', 'string') # Cast to string
NON_EXISTENT = BC.get_parameter('non_existent', 'string') # This item doesn't exists so
                                                          # None will be stored in SUBITEM
DB_PASSWORD =  BC.get_parameter(path='db_password', type='string',
                            decrypt=True) # The DECRYPTED version of db_password will be saved
JAJA_CONFIG = {"as": "b", "cd": "dd"} # For educative intentions
JSON_VALUE = BC.get_parameter(path='weird_config', type='json')
LIST = BC.get_parameter(path='list_of_things', type='code')
DICT = BC.get_parameter(path='python_dict', type='code')
```

Check if a parameter is encrypted or not:

```python
if BC.is_encrypted(path='db_password'):
    print("it is encrypted")
else:
    print("it isn't encrypted")
```


The path of the parameters should be:

**/project/environment/key1/subkey1/subkey2/.../subkeyN**
