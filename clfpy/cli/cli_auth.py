import cmd
import readline
import os

import sys
sys.path.append("../..")

import clfpy as cf

AUTH_endpoint = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
USER_endpoint = "https://api.hetcomp.org/authManager/Users?wsdl"
PROJ_endpoint = "https://api.hetcomp.org/authManager/Projects?wsdl"


class AuthCLI(cmd.Cmd):

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


if __name__ == '__main__':
    AuthCLI().cmdloop()

