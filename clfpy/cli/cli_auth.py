# -*- coding: future_fstrings -*-
import cmd
import readline
import os
import getpass
from builtins import input

import clfpy as cf
from .tools import query_password

AUTH_endpoint = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
USER_endpoint = "https://api.hetcomp.org/authManager/Users?wsdl"
PROJ_endpoint = "https://api.hetcomp.org/authManager/Projects?wsdl"


class AuthCLI(cmd.Cmd, object):

    def __init__(self, token, user, project):
        super(AuthCLI, self).__init__()
        self.session_token = token
        self.user = user
        self.project = project

    def preloop(self):
        self.auth_client = cf.AuthClient(AUTH_endpoint)
        self.user_client = cf.AuthUsersClient(USER_endpoint)
        self.proj_client = cf.AuthProjectsClient(PROJ_endpoint)
        self.update_prompt()

        self.intro = ("This is the CloudFlow authManager client. "
                      "Enter 'help' for more info.")

    def update_prompt(self):
        self.prompt = (f"\n{self.user}@{self.project} – AUTH: ")

    def do_shell(self, arg):
        """Execute a shell command. Usage: shell CMD"""
        os.system(arg)

    def do_exit(self, arg):
        """Exit the application."""
        print('Goodbye')
        return True

    def do_EOF(self, arg):
        """Exit the application."""
        print('Goodbye')
        return True

    def do_get_session_token(self, arg):
        """Obtain a session token. Usage: get_session_token"""
        if arg != "":
            print("Error: Too many arguments")
            return

        username = input("Enter user name: ")
        project = input("Enter project: ")
        password = getpass.getpass("Enter password: ")

        res = self.auth_client.get_session_token(username, project, password)

        if "401: Unauthorized" in str(res):
            print("Error: Login failed")
            return
        else:
            print(res)

    def do_token_info(self, token):
        """Print token info. Usage: token_info [TOKEN]"""
        if token == "":
            print("No TOKEN argument given, using current session token")
            token = self.session_token
        elif len(token.split()) > 1:
            print("Error: Too many arguments")
            return

        print(self.auth_client.get_token_info(token))

    def do_token_info_complete(self, token):
        """Print complete token info. Usage: token_info_complete [TOKEN]"""
        if token == "":
            print("No TOKEN argument given, using current session token")
            token = self.session_token
        elif len(token.split()) > 1:
            print("Error: Too many arguments")
            return

        print(self.auth_client.get_token_info_complete(token))

    def do_validate_token(self, token):
        """Check if a token is valid. Usage: validate_token TOKEN"""
        if token == "":
            print("Error: No TOKEN argument given")
            return
        if len(token.split()) > 1:
            print("Error: Too many arguments")
            return

        print(self.auth_client.validate_session_token(token))

    def do_get_openstack_token(self, token):
        """Obtains the OS token from a workflow token. Usage: get_openstack_token TOKEN"""
        if token == "":
            print("Error: No TOKEN argument given")
            return
        if len(token.split()) > 1:
            print("Error: Too many arguments")
            return

        print(self.auth_client.get_openstack_token(token))

    def do_workflow_count(self, arg):
        """Returns the number of workflows registered in the authManager's database. Usage: workflow_count"""
        if arg != "":
            print("Error: Too many arguments")
            return

        print(self.auth_client.count_workflows())

    def get_portal_token(self):
        try:
            token = os.environ["CFG_PORTAL_TOKEN"]
            return token, True
        except KeyError:
            print("Environment variable CFG_PORTAL_TOKEN must be set for this operation")
            return "", False

    def print_project(self, project):
        print(f"\n{project['name']}")
        print(f"  ID: {project['id']}")
        print(f"  Description: {project['description']}")

    def do_list_projects(self, arg):
        """List all registered projects. Requires set CFG_PORTAL_TOKEN env variable. Usage: list_projects"""
        if arg != "":
            print("Error: Too many arguments")
            return

        token, success = self.get_portal_token()
        if not success:
            return

        res = self.proj_client.list_projects(token)
        for p in res:
            self.print_project(p)

    def do_create_project(self, arg):
        """Create a new project. Requires set CFG_PORTAL_TOKEN env variable. Usage: create_project NAME"""
        args = arg.split()
        if len(args) != 1:
            print("Error: Expected NAME argument")
            return
        name = args[0]

        description = input("Enter project description: ")

        token, success = self.get_portal_token()
        if not success:
            return

        res = self.proj_client.create_project(token, name, description)
        self.print_project(res)

    def do_delete_project(self, arg):
        """Delete a project. Requires set CFG_PORTAL_TOKEN env variable. Usage: delete_project ID"""
        if arg == "":
            print("Error: Argument ID must be given")
            return
        if len(arg.split()) > 1:
            print("Error: Too many arguments")
            return

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.proj_client.delete_project(token, arg))

    def do_list_users(self, arg):
        """List all registered users. Requires set CFG_PORTAL_TOKEN env variable. Usage: list_users"""
        if arg != "":
            print("Error: Too many arguments")
            return

        token, success = self.get_portal_token()
        if not success:
            return

        res = self.user_client.list_users(token)
        for user in res:
            try:
                print(f"\n{user['name']}")
                print(f"  ID: {user['id']}")
                print(f"  Description: {user['description']}")
                print(f"  Email: {user['email']}")
            except AttributeError:
                continue

    def do_create_user(self, arg):
        """Create a new user. Requires set CFG_PORTAL_TOKEN env variable. Usage: create_user NAME PROJECT_ID"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Arguments NAME and PROJECT_ID required")
            return
        name = args[0]
        project_ID = args[1]

        token, success = self.get_portal_token()
        if not success:
            return

        email = input("Enter the user's email address: ")
        description = input("Enter a description: ")
        password = query_password("Enter a password: ")

        print(self.user_client.create_user(token, name, password, email,
              description, project_ID))

    def do_delete_user(self, arg):
        """Delete a user. Requires set CFG_PORTAL_TOKEN env variable. Usage: delete_user ID"""
        if arg == "":
            print("Error: Argument ID must be given")
            return
        if len(arg.split()) > 1:
            print("Error: Too many arguments")
            return

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.delete_user(token, arg))


if __name__ == '__main__':
    AuthCLI().cmdloop()
