# Asynchronous python library for work with Steam

[![pypi: package](https://img.shields.io/badge/pypi-0.0.1-blue)](https://pypi.org/project/pysteamlib/)
[![Imports: isort](https://img.shields.io/badge/imports-isort-success)](https://pycqa.github.io/isort/)
[![Linter: flake8](https://img.shields.io/badge/linter-flake8-success)](https://github.com/PyCQA/flake8)
[![Mypy: checked](https://img.shields.io/badge/mypy-checked-success)](https://github.com/python/mypy)
[![Python: versions](
https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)]()


## Install

```bash
pip install pysteamlib
```

## Usage

```python
import asyncio

from pysteamauth.auth import AuthenticatorData, Steam
from steamlib.api import SteamAPI


async def usage():

    steam = Steam(
        login='login',
        password='password',
        steamid=76561111111111111,
        authenticator=AuthenticatorData(
            shared_secret='shared_secret',
            device_id='device_id',
            identity_secret='identity_secret',
        ),
    )
    await steam.login_to_steam()

    api = SteamAPI(steam)


if __name__ == '__main__':
    asyncio.run(usage())
```
