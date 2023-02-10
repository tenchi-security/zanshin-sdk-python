![ Coverage badge ](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/tenchi-security/zanshin-sdk-python/python-coverage-comment-action-badge.json)
[![PyPI version shields.io](https://img.shields.io/pypi/v/zanshinsdk.svg)](https://pypi.python.org/pypi/zanshinsdk/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/zanshinsdk.svg)](https://pypi.python.org/pypi/zanshinsdk/)

# Zanshin Python SDK

This Python package contains an SDK to interact with the [API of the Zanshin SaaS service](https://api.zanshin.tenchisecurity.com) from [Tenchi Security](https://www.tenchisecurity.com).

This SDK is used to implement a command-line utility, which is available on [Github](https://github.com/tenchi-security/zanshin-cli) and on [PyPI](https://pypi.python.org/pypi/zanshincli/).

## Setting up Credentials

There are three ways that the SDK handles credentials. The order of evaluation is:
- [**1st** Client Parameters](#client-parameters)
- [**2nd** Environment Variables](#environment-variables)
- [**3rd** Config File](#config-file)

### Client Parameters

When calling the `Client` class, you can pass the values API Key, API URL, Proxy URL and User Agent you want to use as below:

```python
from zanshinsdk import Client

client = Client(api_key="my_zanshin_api_key")

print(client.get_me())
```

> :warning: These values will overwrite anything you set as Environment Variables or in the Config File.

### Environment Variables

You can use the following Environment Variables to configure Zanshin SDK:
- `ZANSHIN_API_KEY`: Will setup your Zanshin credentials
- `ZANSHIN_API_URL`: Will define the API URL. Default is `https://api.zanshin.tenchisecurity.com`
- `ZANSHIN_USER_AGENT`: If you want to overwrite the User Agent when calling Zanshin API
- `HTTP_PROXY | HTTPS_PROXY`: Zanshin SDK uses HTTPX under the hood, checkout the [Environment Variables](https://www.python-httpx.org/environment_variables/#proxies) section of their documentation for more use cases

#### Usage

```shell
export ZANSHIN_API_KEY="eyJhbGciOiJIU..."
```

> :warning: These Environment Variables will overwrite anything you set on the Config File.

### Config File
Second is by using a configuration file in the format created by the Python [RawConfigParser](https://docs.python.org/3/library/configparser.html#configparser.RawConfigParser) class.

The file is located at `~/.tenchi/config`, where `~` is the [current user's home directory](https://docs.python.org/3/library/pathlib.html#pathlib.Path.home).

Each section is treated as a configuration profile, and the SDK will look for a section called `default` if another is not explicitly selected.

These are the supported options:

* `api_key` (required) which contains the Zanshin API key obtained at the [Zanshin web portal](https://zanshin.tenchisecurity.com/my-profile).
* `user_agent` (optional) allows you to override the default user-agent header used by the SDK when making API requests.
* `api_url` (optional) directs the SDK to use a different API endpoint than the default (https://api.zanshin.tenchisecurity.com).

This is what a minimal configuration file looks like:
```ini
[default]
api_key = abcdefghijklmnopqrstuvxyz
```

## The SDK

The SDK uses Python 3 type hints extensively. It attempts to abstract API artifacts such as pagination by using Python generators, thus making the service easier to interact with.

The network connections are done using the wonderful [httpx](https://www.python-httpx.org/) library.

Currently it focuses on returning the parsed JSON values instead of converting them into native classes for higher level abstractions.

The `zanshinsdk.Client` class is the main entry point of the SDK. Here is a quick example that shows information about the owner of the API key in use:

```python
from zanshinsdk import Client
from json import dumps

client = Client()   # loads API key from the "default" profile in ~/.tenchi/config
me = client.get_me()    # calls /me API endpoint
print(dumps(me, indent=4))
```

For more examples, checkout the [docs](zanshinsdk/docs/README.md).

All operations call `raise_for_status` on the httpx [Response object](https://www.python-httpx.org/api/#response) internally, so any 4xx or 5xx will raise [exceptions](https://www.python-httpx.org/exceptions/).

## Installing

To install the SDK, you can use `pip`. You have two options to install ZanshinSDK:
- *Essentials*

Using `pip install zanshinsdk` will install the SDK with all features exception ability to perform onboarding of new Scan Targets. For this, you'll need to install boto3.

- *With Boto3*

With `pip install zanshinsdk[with_boto3]` you'll automatically install [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) along with ZanshinSDK. This will enable you to perform Onboard of new Scan Targets via SDK.

## Testing

To run all tests call `make test` on the project root directory. Make sure there's a `[default]` profile configured, else some tests will fail.
Also, be sure to install `boto3` and `moto[all]` or some integration tests will fail.

# Support

If you are a Zanshin customer and have any questions regarding the use of the service, its API or this SDK package, please get in touch via e-mail at support {at} tenchisecurity {dot} com or via the support widget on the [Zanshin Portal](https://zanshin.tenchisecurity.com).
