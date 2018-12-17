import cmd
import readline
import os

import sys
sys.path.append("../..")

import clfpy as cf

SERVICES_endpoint = "https://api.hetcomp.org/servicectl-1"


class ServicesCLI(cmd.Cmd):

    def __init__(self, token, user, project):
        super(ServicesCLI, self).__init__()
        self.session_token = token
        self.user = user
        self.project = project

    def preloop(self):
        self.srv = cf.ServicesClient(SERVICES_endpoint)
        self.update_prompt()

        self.intro = ("This is the CloudFlow services client. "
                      "Enter 'help' for more info.")


    def update_prompt(self):
        self.prompt = (f"\n{self.user}@{self.project} – SERVICES: ")

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

    def do_ls(self, arg):
        """List available services. Usage: ls"""
        services = self.srv.list_services(self.session_token)
        for s in services:
            print(f"{s['name']}")

    def do_status(self, service):
        """Show status for a service. Usage: status SERVICE"""
        self.srv.print_service_status(self.session_token, service)


if __name__ == '__main__':
    ServicesCLI().cmdloop()

