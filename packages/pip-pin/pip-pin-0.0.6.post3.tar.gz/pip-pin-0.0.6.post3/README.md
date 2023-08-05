THIS IS AN EXPERIMENT. PLAY WITH IT, THINK ABOUT IT, DON'T USE IT ON PRODUCTION.

Let me know what you think.

[![PyPI version shields.io](https://img.shields.io/pypi/v/pip-pin.svg)](https://pypi.python.org/pypi/pip-pin/)

[![PyPI status](https://img.shields.io/pypi/status/pip-pin.svg)](https://pypi.python.org/pypi/pip-pin/)

pip pin
=======

Specify and pin dependencies from `setup.py`.

TL;DR;

```python
from setuptools import find_packages, setup

setup(
    name='meriadok',
    version='1.0.',
    packages=find_packages(),
    setup_requires=[
        'pip-pin',
    ],
    install_requires=[
        'flask',
    ],
    tests_require=[
        'pytest',
    ],
    develop_requires=[
        'black',
    ],
)
```

Non-pinned dependencies:
------------------------

Just install whatever you want with `pip`.

Pinning
-------

This will produce (or update) `.pip-pin` directory, which you are supposed to commit into the repo.

```
$ ./setup.py pin [(--install|--tests|--develop)]
```

Note that this will pin *only* things listed in a respective `setup.py`
section. This means you can have additional stuff installed on your local
virtualenv, and noone is going to care until you make it a dependency.

Pinned dependencies:
--------------------

Installing pinned dependencies:

```
$ ./setup.py sync [(--install|--tests|--develop)]

```
