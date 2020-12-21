# -*- coding: future_fstrings -*-
from __future__ import print_function
import cmd
import readline
import os

import clfpy as cf
from .tools import query_yes_no, query_int, query_filepath

SERVICES_endpoint = "https://api.hetcomp.org/servicectl-1"


class ServicesCLI(cmd.Cmd, object):

    def __init__(self, token, user, project):
        super(ServicesCLI, self).__init__()
        self.session_token = token
        self.user = user
        self.project = project
        self.last_ls_names = []
        self.last_ls_deplpaths = []

    def preloop(self):
        self.srv = cf.ServicesClient(SERVICES_endpoint)
        self.update_prompt()
        self.make_service_list()

        self.intro = ("This is the CloudFlow services client. "
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

    def make_service_list(self):
        services = self.srv.list_services(self.session_token)
        self.last_ls_names = []
        self.last_ls_deplpaths = []
        for s in services:
            name = s['name']
            depl_path = [link['href'] for link in s['links'] if link['rel'] == 'deployment'][0]
            self.last_ls_names.append(name)
            self.last_ls_deplpaths.append(depl_path)

    def name_completion(self, text, line, begidx, endidx):
        """Implements completion of service names.

        This algorithm makes sure that completion works also when a partial
        name is already typed and more than one service beginning with that
        partial name exists.
        """
        parts = line.split(' ', 1)
        if len(parts) > 1 and parts[1] != '':
            if text == '':
                prefix = parts[1]
            else:
                prefix = parts[1][:-len(text)]
            candidates = [n[len(prefix):] for n in self.last_ls_names if n.startswith(prefix)]
        else:
            candidates = self.last_ls_names
        matches = [n for n in candidates if n.startswith(text)]
        if len(matches) == 1:
            matches[0] += ' '
        return matches

    def do_ls(self, arg):
        """List available services. Usage: ls"""
        self.make_service_list()
        if len(self.last_ls_names) == 0:
            print("No services available in this project")
            return
        for i, n in enumerate(self.last_ls_names):
            print(f"  {n:<30} Deployment URL: {self.last_ls_deplpaths[i]}")

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
        except (cf.MethodNotAllowedException, cf.BadRequestException) as err:
            print(f"Error: {err}")
            return

        self.make_service_list()
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

        self.make_service_list()
        print(f"Service {name} removed")

    complete_remove = name_completion

    do_rm = do_remove
    complete_rm = name_completion

    def help_rm(self):
        print("(Same as 'remove') Remove a service and all its resources. Usage: rm NAME")

    def do_status(self, service):
        """Show status for a service. Usage: status SERVICE"""
        if service == "":
            print("Error: Service name must be given")
            return
        if len(service.split()) > 1:
            print("Error: Too many arguments")
            return
        self.srv.print_service_status(self.session_token, service)

    complete_status = name_completion

    def do_logs(self, arg):
        """Show logs for a service. Usage: logs NAME [N_EVENTS] [N_LOG_STREAMS]"""
        if arg == "":
            print("Error: At least a service name must be given")
            return
        if len(arg.split()) > 3:
            print("Error: Too many arguments")
            return

        args = arg.split()
        name = args[0]
        tail = 20
        streams = 1
        try:
            if len(args) > 1:
                tail = int(args[1])
            if len(args) > 2:
                streams = int(args[2])
        except ValueError:
            print(f"Error: Arguments after '{name}' must be integers")
            return

        self.srv.print_service_logs(self.session_token, name, tail, streams)

    complete_logs = name_completion

    def do_push_docker_image(self, arg):
        """Build and push a Docker image to a service repo. Usage: push_docker_image NAME DOCKER_SRC_FOLDER"""
        args = arg.split()
        if len(args) != 2:
            print(f"Error: Expected 2 arguments, {len(args)} given")
            return
        name = args[0]
        docker_src_folder = args[1]

        try:
            creds = self.srv.get_docker_credentials(self.session_token, name)
        except cf.ServiceNotFoundException:
            print(f"Error: Service '{name}' doesn't exist")
            return

        self.srv.build_and_push_docker_image(self.session_token, name,
                                             docker_src_folder, creds)

    complete_push_docker_image = name_completion

    def do_pull_docker_image(self, arg):
        """Pulls a service's Docker image. Usage: pull_docker_image NAME"""
        args = arg.split()
        if len(args) != 1:
            print(f"Error: Expected 1 argument, {len(args)} given")
            return
        name = args[0]

        try:
            creds = self.srv.get_docker_credentials(self.session_token, name)
        except cf.ServiceNotFoundException:
            print(f"Error: Service '{name}' doesn't exist")
            return

        self.srv.pull_docker_image(self.session_token, name, creds)

    complete_pull_docker_image = name_completion

    def do_update(self, name):
        """Update an existing service. Usage: update NAME"""
        if len(name.split()) > 1:
            print("Error: Too many arguments")
            return
        if name == "":
            print("Error: No service name given")
            return

        try:
            status = self.srv.get_service_status(self.session_token, name)["status"]
        except cf.ServiceNotFoundException:
            print(f"Error: Service {name} doesn't exist")
            return

        create_new_taskdef = True
        mem_res = 50
        mem_lim = 75
        port = 80
        if len(status['tasks']) > 0:
            task = status['tasks'][0]
            taskdef = task['task_definition']
            mem_res = int(taskdef['container_memory_reservation'])
            mem_lim = int(taskdef['container_memory_limit'])
            port = int(taskdef['container_port'])
            print("Found the following existing service definition:")
            print(f"  Memory reservation: {mem_res} MB")
            print(f"  Memory limit: {mem_lim} MB")
            print(f"  Container port: {port}")
            create_new_taskdef = query_yes_no("Do you want to create a new service definition?", "no")

        if create_new_taskdef:
            mem_res = query_int("Enter memory reservation (MB)", mem_res)
            mem_lim = query_int("Enter memory limit (MB)", mem_lim)
            port = query_int("Enter container port", port)

        env_path = query_filepath("Enter path to environment-definition file")
        env = self.srv.read_env_file(env_path)

        service_def = {
            'container-tag': 'latest',
            'memory-reservation': mem_res,
            'memory-limit': mem_lim,
            'container-port': port,
            'environment': env
        }

        self.srv.update_service(self.session_token, name, service_def)

    complete_update = name_completion


if __name__ == '__main__':
    ServicesCLI().cmdloop()
