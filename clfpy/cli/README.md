# Command-line interface for the clfpy library
clfpy comes with a command-line interface (CLI) which allows you to use the
full library functionality interactively.

## Installation
The command-line interface is automatically installed when you install the
clfpy library using `pip install clfpy`.

## Invocation
If the library is installed, you can run the CLI from any terminal:
```
$ clfpy_cli
```

## Logging in
The clfpy CLI needs valid user credentials to access the SemWES platform.
You can provide these credentials in three different ways:

1. Interactive login: If you simply start the CLI, you will be asked for
   username, project, and password.
2. Credentials in environment variables: The clfpy CLI will check if the three
   environment variables `CFG_USERNAME`, `CFG_PROJECT`, and `CFG_PASSWORD` are
   set.  If yes, it will skip the interactive login and use the values of these
   variables instead.
3. Session token in environment variables: If you already have a session token,
   you can store it in the `CFG_TOKEN` environment variable. The clfpy CLI will
   then skip the login process altogether and use this token instead.

## Basic commands
The following commands are available at all times in the clfpy CLI:
* `help` or `?`: Display all currently available commands
* `? <command>`: Display a command's help
* `! <command>`: Break out of the clfpy CLI and execute `<command>` in the
  underlying shell.
* `exit` or `Ctrl-D`: Exit the current client

## Tab completion
Most of the CLI's commands allow tab completion. Simply type parts of a command
followed by one or two TABs to complete the command or show a list of
completion options, respectively.

## Choosing a client
Just like the clfpy library, the CLI is divided into several clients. After
starting the CLI, you need to select a client with the command `client <name>`.
As an example, `client gss` switches to the GSS client which allows you to
browse files and folders on GSS. Typing `exit` or `Ctrl-D` exits a client and
brings you back to the client-selection stage.

## Example commands
The following is a list of commonly used commands, sorted by client. Please
explore the in-built help to discover the fully set of commands.

### Client `gss`: File handling
* `ls` or `dir`: List files in current folder
* `cd <folder>`: Change directory
* `dl <path>`: Download a file
* `ul <path>`: Upload a file
* `mkdir <folder>`: Create a directory
* `rm <path>`: Remove a file or folder
* `list_storages`: List available storages (such as `it4i_anselm://`)
* `set_storage <storage_identifier>`: Change storage
* `img_ls`: List Singularity images registered for the current cluster
* `img_register <file>`: Directly register a file as a Singularity image

### Client `images`: Singularity-image management
* `ls`: List images registered on the current cluster
* `list_clusters`: List available clusters
* `set_cluster <cluster_identifier>`: Set cluster
* `register`: Register a new image
* `update`: Update an existing image
* `rm <image>`: De-register an image

### Client `services`: Service management
* `ls`: List currently registered services
* `create_new`: Create a new service
* `push_docker_image`: Push a docker image for a service
* `update`: Update a service
* `status`: Get a service's status
* `logs`: Get a service's logs
* `rm` or `remove`: Remove a service

### Client `auth`: Authentication and user management
* `get_session_token`: Obtain a session token (== log into the platform)
* `token_info`: Show information connected to the current session token
* `validate_token <token>`: Check if the given token is valid
* `change_password`: Change the password of the currently logged-in user
* `update_email`: Set a new email address for the currently logged-in user
