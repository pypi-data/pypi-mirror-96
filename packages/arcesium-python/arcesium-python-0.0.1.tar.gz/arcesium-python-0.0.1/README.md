# Arcesium Python Client Guider

The purpose of this package is to guide clients on how to find and install a
full version of the Arcesium Python client while offering a space to add
functionality for new developers at clients.

We add an import finder to the import meta_path so that anything imported from
the arcesium namespace gives a warning and guidance on how to download the 
correct library.

## sample output ##

```
>>> from arcesium.moss.service.transaction import TransactionService
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'arcesium.moss' cannot be imported from the pypi package
To use the Arcesium Python Client library services
please install from https://downloads.arcesium.com
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/codemill/katzm/poc/dummy_arcesium_python/arcesium/__init__.py", line 28, in find_spec
    raise ModuleNotFoundError(error_str)
ModuleNotFoundError: Please reinstall arcesium-python from https://downloads.arcesium.com
>>> from arcesium.paw import foo
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'arcesium.paw' cannot be imported from the pypi package
To use the Arcesium Python Client library services
please install from https://downloads.arcesium.com
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/codemill/katzm/poc/dummy_arcesium_python/arcesium/__init__.py", line 28, in find_spec
    raise ModuleNotFoundError(error_str)
ModuleNotFoundError: Please reinstall arcesium-python from https://downloads.arcesium.com
>>>


```
