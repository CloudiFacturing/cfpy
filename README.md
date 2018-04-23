# `cfpy` – Python library for accessing infrastructure services in CloudFlow and its derivatives
This is a simple Python library that offers access to infrastructure services
in CloudFlow and its derivatives.

## Implemented clients
Currently, the following clients are available:
* `cfpy.AuthClient`: Client for the authentication manager
* `cfpy.AuthUsersClient`: Client for the users interface of the authentication
  manager
* `cfpy.AuthProjectsClient`: Client for the projects interface of the
  authentication manager
* `cfpy.GssClient`: Client for accessing the generic storage services (GSS)

## Requirements
Requires Python 2.7 or Python 3.x.

## Installation
Download library and install using pip (from the directory containing this
readme):
```
pip install -e .
```
This will install the necessary dependencies

## How to use
Have a look at the `cfpy/tests/` folder to find examples on how to use the library.
