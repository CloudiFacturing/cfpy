# -*- coding: future_fstrings -*-
import cmd
import readline
import os
import getpass
from builtins import input

import clfpy as cf
from .tools import query_password, query_yes_no

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

    def completenames(self, text, *ignored):
        """Overrides the original method for command completion.

        Adds a space to the matches if there is only one match, which results
        in a smoother experience.
        """
        dotext = 'do_'+text
        matches = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        if len(matches) == 1:
            matches[0] += ' '
        return matches

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

    def do_add_user_to_project(self, arg):
        """Adds a user to a project. Requires set CFG_PORTAL_TOKEN env variable. Usage: add_user_to_project USER_ID PROJECT_ID"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Arguments USER_ID and PROJECT_ID required")
            return
        user_ID = args[0]
        project_ID = args[1]

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.add_user_to_project(token, user_ID,
                                                   project_ID))

    def do_roles_ls(self, arg):
        """Lists all available roles. Requires set CFG_PORTAL_TOKEN env variable. Usage: roles_ls"""
        if arg != "":
            print("Error: Too many arguments")
            return

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.list_possible_roles(token))

    def do_roles_ls_assigned(self, arg):
        """Lists roles assigned to a user. Requires set CFG_PORTAL_TOKEN env variable. Usage: roles_ls_assigned USER_ID PROJECT_ID"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Arguments USER_ID and PROJECT_ID required")
            return
        user_ID = args[0]
        project_ID = args[1]

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.list_roles_for_user_in_project(token, user_ID,
                                                              project_ID))

    def do_roles_assign(self, arg):
        """Assigns a role to a user. Requires set CFG_PORTAL_TOKEN env variable. Usage: roles_assign USER_ID PROJECT_ID ROLE_NAME"""
        args = arg.split()
        if len(args) != 3:
            print("Error: Arguments USER_ID, PROJECT_ID, and ROLE_NAME required")
            return
        user_ID = args[0]
        project_ID = args[1]
        role_name = args[2]

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.assign_role_to_user(token, user_ID, project_ID,
                                                   role_name))

    def do_roles_withdraw(self, arg):
        """Withdraws a role from a user. Requires set CFG_PORTAL_TOKEN env variable. Usage: roles_withdraw USER_ID PROJECT_ID ROLE_NAME"""
        args = arg.split()
        if len(args) != 3:
            print("Error: Arguments USER_ID, PROJECT_ID, and ROLE_NAME required")
            return
        user_ID = args[0]
        project_ID = args[1]
        role_name = args[2]

        token, success = self.get_portal_token()
        if not success:
            return

        print(self.user_client.withdraw_role_from_user(token, user_ID,
                                                       project_ID, role_name))

    def do_change_password(self, arg):
        """Change the password of the logged-in user. Usage: change_password"""
        if arg != "":
            print("Error: Too many arguments")
            return

        confirm = query_yes_no("Warning: After changing your password, you will be logged out of the CLI. Continue?")
        if not confirm:
            return

        tk_info = self.auth_client.get_token_info(self.session_token)
        user_id = tk_info['user']['id']

        old_password = query_password("Old password: ")
        new_password = query_password("New password: ")

        success = self.user_client.change_password(self.session_token, user_id,
              old_password, new_password)

        if success:
            print("Password changed successfully. You will be logged out now.")
            exit(0)

    def do_update_email(self, arg):
        """Change the email address of the logged-in user. Usage: update_email"""
        if arg != "":
            print("Error: Too many arguments")
            return

        new_email = input("Enter new email address: ")

        success = self.user_client.update_email(self.session_token, new_email)
        if success:
            print("Email updated successfully")
        else:
            print("Something went wrong during the update")


if __name__ == '__main__':
    AuthCLI().cmdloop()
