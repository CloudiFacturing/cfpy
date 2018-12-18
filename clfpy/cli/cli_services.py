import cmd
import readline
import os

import sys
sys.path.append("../..")

import clfpy as cf

from cli_tools import query_yes_no

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
        if len(services) == 0:
            print("No services available in this project")
        for s in services:
            name = s['name']
            depl_path = [link['href'] for link in s['links'] if link['rel'] == 'deployment'][0]
            print(f"  {name:<30} Deployment URL: {depl_path}")

    def do_create_new(self, name):
        """Create a new service. Usage: create_new NAME"""
        if len(name.split()) > 1:
            print("Error: Too many arguments")
            return
        if name == "":
            print("Error: No service name given")
            return

        print(f"New service {name} will be created with a standard health "
              "check on the deployment path, accepting HTTP response codes "
              "200-499.")
        custom_health_check = query_yes_no("Do you want to define a custom "
                                           "health check?", "no")

        if custom_health_check:
            print("Custom halth check not available")

        try:
            res = self.srv.create_new_service(self.session_token, name)
        except cf.MethodNotAllowedException as err:
            print(f"Error: {err}")
            return

        print(f"Created new service {name}")

    def do_remove(self, name):
        """Remove a service and all its resources. Usage: remove NAME"""
        if len(name.split()) > 1:
            print("Error: Too many arguments")
            return
        if name == "":
            print("Error: No service name given")
            return

        confirm = query_yes_no(f"This will stop and remove '{name}' including "
                               "all its Docker images. Continue?", "no")
        if not confirm:
            print("Cancelled")
            return

        try:
            self.srv.delete_service(self.session_token, name)
        except cf.ServiceNotFoundException:
            print(f"Error: Service {name} not found")
            return

        print(f"Service {name} removed")

    def do_status(self, service):
        """Show status for a service. Usage: status SERVICE"""
        self.srv.print_service_status(self.session_token, service)


if __name__ == '__main__':
    ServicesCLI().cmdloop()

