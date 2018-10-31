# `clfpy` – Python library for accessing infrastructure services in CloudFlow and its derivatives
This is a simple Python library that offers access to infrastructure services
in CloudFlow and its derivatives. The library aims to make things like
interaction with GSS (file upload, download, etc.) as easy and hassle-free as
possible.

## Changelog
###2018-10-31: Version 0.7
* Bugfix: Uploading an empty file fails

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

## Requirements
Requires Python 2.7 or Python 3.x.

## Installation
`clfpy` can be installed from the Python Package Index using pip:
```shell
pip install clfpy
```

## How to use
Have a look at the `clfpy/tests/` folder to find examples on how to use the
library.
