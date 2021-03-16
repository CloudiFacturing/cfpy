# `clfpy` – Python library for accessing platform services of the SemWES platform
This is a simple Python library that offers access to infrastructure services
in SemWES (formerly CloudFlow) and its derivatives. The library aims to make
things like interaction with GSS (file upload, download, etc.) as easy and
hassle-free as possible.

## Command-line interface (CLI)
With version 1.0.0 of the library, a command-line interface was added for fully
interactive use. Simply install clfpy with pip and then execute `clfpy_cli`
from any terminal. For more detailed documentation, check the CLI's [readme
page](./clfpy/cli/README.md).

A big thank you goes to Leonardo Cosma from CETMA who initiated the creation of
the CLI and also provided some of the code.

## Changelog
### 2021-03-16: Version 1.3.2
* (BUGFIX) Removed Anselm and Salomon support, fixing broken images client.

### 2020-12-21: Version 1.3.1
* (BUGFIX) Fixed Barbora support

### 2020-12-21: Version 1.3.0
* (MINOR) Added support for Barbora cluster

### 2020-10-12: Version 1.2.0
* (MINOR) Added method to services client to pull a Docker image

### 2019-04-24: Version 1.1.3
* (PATCH) Fix bad hardcoded interpreter in clfpy_cli script

### 2019-03-29: Version 1.1.2
* (PATCH) Re-brand CloudFlow to SemWES

### 2019-01-17: Version 1.1.1
* (PATCH) Fix CLI tab completion for service names

### 2019-01-16: Version 1.1.0
* (MINOR) Added missing methods to CLI auth client
* (MINOR) Improved tab completion in the CLI

### 2019-01-07: Version 1.0.1
* (PATCH) Fixed broken input for Python 2.7

### 2019-01-07: Version 1.0.0
* (MAJOR) Added full command-line interface for the library
* (MINOR) Added missing list_users method to `clfpy.AuthUsersClient`
* (PATCH) Added better exception handling to `clfpy.ServicesClient` and `clfpy.HpcImagesClient`

### 2018-12-14: Version 0.10.1
* (PATH) Added exception handling to `clfpy.ServicesClient`.

### 2018-12-11: Version 0.10.0
* (MINOR) Added `clfpy.ExtraParameters` class for parsing extraParameters
  strings
* (PATCH) Fixed Python 2.x problem for `clfpy.ServicesClient`.

### 2018-12-10: Version 0.9.0
* (MINOR) Added convenience function `clfpy.ServicesClient.read_env_file()` for
  reading environment-definition files when defining services.

### 2018-12-07: Version 0.8.1
* (PATCH) `clfpy.ServicesClient`: Added health description in case of unhealthy
  targets.

### 2018-12-07: Version 0.8.0
* (MINOR) New client `clfpy.ServicesClient` for automatic service deployment in
  CloudFlow
* (PATCH) Fixed HPC endpoint in `test_hpy.py`

### 2018-11-27: Version 0.7.0
* (MINOR) File upload and download now shows a status bar and the average speed
  by default.

### 2018-10-31: Version 0.6.2
* (PATCH) Bugfix: GSS test script fails with Python 2.7

### 2018-10-31: Version 0.6.1
* (PATCH) Bugfix: Uploading an empty file fails

## Implemented clients
Currently, the following clients are available:
* `clfpy.AuthClient`: Client for the authentication manager
* `clfpy.AuthUsersClient`: Client for the users interface of the authentication
  manager
* `clfpy.AuthProjectsClient`: Client for the projects interface of the
  authentication manager
* `clfpy.GssClient`: Client for accessing the generic storage services (GSS)
* `clfpy.HpcImagesClient`: Client for registering Singularity images with the
  CloudFlow HPC client
* `clfpy.WfmClient`: Client for interacting with the workflow manager (does not
  yet expose the full WFM functionality)
* `clfpy.ServicesClient`: Client for automatic service deployment. _Requires
  Docker to be installed!_

Furthermore, use `clfpy.ExtraParameters` for parsing extraParameters inputs in
your services.

## Requirements
Requires Python 2.7 or Python 3.x.

For the `clfpy.ServicesClient`, Docker must be installed as well and the 
Docker CLI must be available under the `docker` command.

## Installation
`clfpy` can be installed from the Python Package Index using pip:
```shell
pip install clfpy
```

## How to use
Have a look at the `clfpy/tests/` folder to find examples on how to use the
library.

## Development
### How to upload a new version to PyPi
1. Make changes to the code
2. Run test scripts with Python 2.7 _and_ Python 3.x.
3. Update the changelog and choose a new version number using semantic
   versioning.
4. Update the version number in `setup.py`.
5. Remove all files from `./dist` and `./build` to avoid attempting to
   overwrite existing files when uploading.
6. Run `python setup.py sdist bdist_wheel` and check the resulting files in
   `./dist`.
7. Run `twine upload dist/*` to upload to PyPi.
   Note that this step requires a correctly configured `~/.pypirc` file.
