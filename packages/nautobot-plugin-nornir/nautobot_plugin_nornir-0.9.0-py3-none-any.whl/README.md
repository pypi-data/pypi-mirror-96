# ntc-nautobot-plugin-nornir

A plugin for [Nautobot](https://github.com/nautobot/nautobot).

## Installation

The plugin is available as a Python package in pypi and can be installed with pip
```shell
pip install nautobot-plugin-nornir
```

> The plugin is compatible with Nautobot 1.0.0 and higher
 
To ensure Nautobot Nornir Plugin is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot_nornir` package:

```no-highlight
# echo nautobot-plugin-nornir>> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `configuration.py`
```python
# In your configuration.py
PLUGINS = ["nautobot_nornir"]

PLUGINS_CONFIG = {
  "nautobot_nornir": {
    "nornir_settings": {
      "credentials": "nautobot_nornir.credentials.env_vars.CredentialsEnvVars",
      "nornir.core": {"num_workers": 10},
      "runner": {
        "plugin": "threaded",
        "options": {
            "num_workers": 10,
        },
      },
    },
  }
```

The plugin behavior can be controlled with the following list of settings

- TODO

## Usage

### API

TODO

## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guideline and is leveraging:
- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`. 

Each command can be executed with `invoke <command>`. All commands support the arguments `--nautobot-ver` and `--python-ver` if you want to manually define the version of Python and Nautobot to use. Each command also has its own help `invoke <command> --help`

#### Local dev environment
```
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility 
```
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```
#### Testing 

```
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).
Sign up [here](http://slack.networktocode.com/)

## Screenshots

TODO

## Initial very basic usage

```
from nornir import InitNornir

PLUGIN_SETTINGS = {
    "inventory": "nautobot_nornir.inventory.nautobot_orm.NautobotORMInventory",
    "credentials": "nautobot_nornir.credentials.env_vars.CredentialsEnvVars",
    "nornir.core": {"num_workers": 10},
    "inventory_params" : {
        "use_fqdn": True,
        "fqdn": "example.com",
    },
}

nornir = InitNornir(
    core=PLUGIN_SETTINGS.get("nornir.core"),
    logging={"enabled": False},
    inventory={
        "plugin": PLUGIN_SETTINGS.get("inventory"),
        "options": {
            "credentials_class": PLUGIN_SETTINGS.get("credentials"),
            "params": PLUGIN_SETTINGS.get("inventory_params"),
            "queryset": self.queryset,
        },
    },
)
```
