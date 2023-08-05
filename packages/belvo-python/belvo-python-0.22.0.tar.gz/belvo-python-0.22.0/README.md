<h1 align="center">Belvo Python SDK</h1>
<p align="center">
    <a href="https://pypi.org/project/belvo-python/"><img alt="PyPI" src="https://img.shields.io/pypi/v/belvo-python?style=for-the-badge"></a>
    <a href="https://pypistats.org/packages/belvo-python"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/belvo-python?style=for-the-badge"></a>
    <a href="https://travis-ci.com/belvo-finance/belvo-python"><img alt="Travis (.com)" src="https://img.shields.io/travis/com/belvo-finance/belvo-python/master?style=for-the-badge"></a>
    <a href="https://coveralls.io/github/belvo-finance/belvo-python"><img alt="Coveralls github" src="https://img.shields.io/coveralls/github/belvo-finance/belvo-python?style=for-the-badge"></a>
    <a href="https://github.com/psf/black"><img alt="Coveralls github" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge"></a>
</p>

## 📕 Documentation
How to use `belvo-python`: https://belvo-finance.github.io/belvo-python/

If you want to check the full documentation about Belvo API: https://docs.belvo.com

Or if you want to more information about:
* [Getting Belvo API keys](https://developers.belvo.com/docs/get-your-belvo-api-keys)
* [Using Connect Widget](https://developers.belvo.com/docs/connect-widget)
* [Testing in sandbox](https://developers.belvo.com/docs/test-in-sandbox)
* [Using webhooks and recurrent links](https://developers.belvo.com/docs/webhooks)


## 📋 Requirements
* Python 3.6+

## 🚀 Getting started

Install using `pip`:
```
$ pip install belvo-python
```

## Example
```python

from pprint import pprint

from belvo.client import Client
from belvo.enums import AccessMode

# Login to Belvo API
client = Client("my-secret-key-id", "my-secret-key", "https://api.belvo.com")

# Register a link 
link = client.Links.create(
    institution="banamex",
    username="johndoe",
    password="supersecret",
    access_mode=AccessMode.SINGLE
)

# Get all accounts
client.Accounts.create(link["id"])

# Pretty print all checking accounts
for account in client.Accounts.list(type="checking"):
    pprint(account)
```

## 🐍 Development

To release a new version of the SDK to PyPI:
- Use `make new-version major|minor|patch` to bump a new version.
- Create a new pull request for the new version.
- Once the new version is merged in `master`, create a `tag` matching the new version.

## 👥 Contributing
**Anyone** can do something to make `belvo-python` better, so contributors are always welcome!
For more details about contributing to this project, please take a look to our [guidelines](CONTRIBUTING.md). 
