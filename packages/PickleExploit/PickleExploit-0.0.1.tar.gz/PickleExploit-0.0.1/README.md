# PickleExploit

## Description
This package implement a Pickle Exploit Builder.

## Requirements
This package require :
 - python3
 - python3 Standard Library

## Installation
```bash
pip install PickleExploit
```

## Examples

1. Code for python paylaod:
 ```python
 pyexploit = PyPickleExploit("print('je test', 'test2')")
 pyexploit.build()
 exploit_pickled = pyexploit.get_pickle_payload()
 pyexploit.execute_payload()
 ```
2. Output:
 ```
 je test test2
 ```

1. Code for command paylaod:
 ```python
 shellexploit = ShellPickleExploit('echo je test')
 shellexploit.build()
 exploit_pickled = shellexploit.get_pickle_payload()
 shellexploit.execute_payload(exploit_pickled) # write "je test" and return the command error code (0)
 ```
2. Output:
 ```
 je test
 0
 ```

## Links
[Github Page](https://github.com/mauricelambert/PickleExploit)
[Documentation](https://mauricelambert.github.io/info/python/security/PickleExploit.html)

## Licence
Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).