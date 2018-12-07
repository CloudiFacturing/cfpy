# -*- coding: utf-8 -*-
"""Lightweight REST client to communicate with servicectl"""
import os
import requests
from subprocess import Popen, PIPE


class ServicesClient():
    """Lightweight servicectl REST client

    Create by passing a the URL to the servicectl server:
        srv = ServicesClient(<url>)
    """

    def __init__(self, url):
        self.url = url

    def _make_auth_header(self, session_token):
        return {"X-Auth-Token": session_token}

    def list_services(self, session_token):
        """Returns a list of services associated with the user's project."""
        this_url = os.path.join(self.url, 'services')
        r = requests.get(
            this_url,
            headers=self._make_auth_header(session_token)
        )
        return r.json()

    def print_service_list(self, session_token):
        """Prints the services associated with the user's project"""
        services = self.list_services(session_token)

        print("\n{} services currently available:".format(len(services)))
        for elem in services:
            print(elem['name'])
            for link in elem['links']:
                if link['rel'] == 'deployment':
                    print("  Deployment path: {}".format(link['href']))

    def create_new_service(self, session_token, name, health_check=None):
        """Creates a new service on CloudFlow

        The optional health check must be a Python dict with the following
        keys: 'rel_path', 'status_codes', 'interval'
        """
        if health_check is None:
            payload = {'name': name}
        else:
            assert('rel_path' in health_check)
            assert('status_codes' in health_check)
            assert('interval' in health_check)
            payload = {
                'name': name,
                'health_check': health_check
            }
        this_url = os.path.join(self.url, 'services')
        r = requests.post(
            this_url,
            headers=self._make_auth_header(session_token),
            json=payload
        )
        return r.json()

    def get_service_status(self, session_token, service_name):
        """Returns a service's status as a Python dict"""
        this_url = os.path.join(self.url, 'services/{}'.format(service_name))
        r = requests.get(
            this_url,
            headers=self._make_auth_header(session_token)
        )
        return r.json()

    def print_service_status(self, session_token, service_name):
        """Prints a service's status in a human-readable way"""
        status = self.get_service_status(session_token, service_name)
        status = status['status']

        print("\nStatus report for service {}:".format(service_name))
        print('Service status: {}'.format(status['service_status']))
        print('Desired count: {}'.format(status['count_desired']))
        print('Running count: {}'.format(status['count_running']))
        print('Pending count: {}'.format(status['count_pending']))
        print('\nTasks:')

        tasks = status['tasks']
        for task in tasks:
            print(task['task_name'])
            print('  Created: {}'.format(task['created_at']))
            print('  Desired status: {}'.format(task['desired_status']))
            print('  Last status: {}\n'.format(task['last_status']))
            print('  Task definition:')
            task_def = task['task_definition']
            print('    Name: {}'.format(task_def['name']))
            print('    Revision: {}'.format(task_def['revision']))
            print('    Status: {}'.format(task_def['status']))
            print('    Container image: {}'.format(task_def['container_image']))
            print('    Container memory reservation: {}'.format(task_def['container_memory_reservation']))
            print('    Container memory limit: {}'.format(task_def['container_memory_limit']))
            print('    Container port: {}'.format(task_def['container_port']))

        print('\nLast events:')
        events = status['events']
        for event in events:
            print('{}: {}'.format(event['created_at'], event['message']))

        print('\nTarget health:')
        t_health = status['target_health']
        print('Health-check path: {}'.format(t_health['health_check_path']))
        print('Health-check interval: {}'.format(t_health['interval']))
        print('Health-check status codes: {}'.format(t_health['status_codes']))
        targets = t_health['targets']
        for i, t in enumerate(targets):
            if 'description' in t:
                print('Target {}/{}: {}, Port: {}, Health: {}, Description: {}'.format(
                    i+1, len(targets), t['target'], t['port'], t['health'], t['description']))
            else:
                print('Target {}/{}: {}, Port: {}, Health: {}'.format(
                    i+1, len(targets), t['target'], t['port'], t['health']))

    def get_service_logs(self, session_token, service_name, tail=20, streams=1):
        """Returns a service's logs as a Python dict"""
        this_url = os.path.join(self.url, 'services/{}'.format(service_name))
        params = {"view": "logs", "tail": tail, "streams": 1}
        r = requests.get(
            this_url,
            headers=self._make_auth_header(session_token),
            params=params
        )
        return r.json()

    def print_service_logs(self, session_token, service_name, tail=20, streams=1):
        """Prints a service's logs in a human-readable way"""
        logs = self.get_service_logs(session_token, service_name, tail, streams)
        logs = logs['logs']

        print("\nPrinting logs for service '{}'".format(service_name))
        print("Printing the last {} log events for the last {} log streams".format(tail, streams))
        for i, log in enumerate(logs):
            print("\nEvents for log stream {}/{} - {}:".format(i+1, len(logs), log['stream_name']))
            for event in log['log_events']:
                print("{}: {}".format(event['time'], event['message']))

    def get_docker_credentials(self, session_token, service_name):
        """Returns a service's Docker credentials as a Python dict"""
        this_url = os.path.join(self.url, 'services/{}'.format(service_name))
        params = {"view": "docker"}
        r = requests.get(
            this_url,
            headers=self._make_auth_header(session_token),
            params=params
        )
        return r.json()

    def build_and_push_docker_image(self, session_token, service_name,
            docker_source_folder, docker_credentials, tag='latest'):
        """Builds and pushes a Docker image to the service's repository"""

        repo_uri = docker_credentials['repo_uri']
        user = docker_credentials['user']
        password = docker_credentials['password']
        proxy_endpoint = docker_credentials['proxy_endpoint']

        this_dir = os.getcwd()
        try:
            print('Logging into Docker repository')
            run_with_output(['docker', 'login', '-u', user, '-p', password,
                            proxy_endpoint])

            os.chdir(docker_source_folder)

            print('Building Docker image')
            tag_local = '{}:{}'.format(service_name, tag)
            run_with_output(['docker', 'build', '-t', tag_local, '.'])

            print('Tagging Docker image')
            tag_remote = '{}:{}'.format(repo_uri, tag)
            run_with_output(['docker', 'tag', tag_local, tag_remote])

            print('Pushing image to the repository')
            run_with_output(['docker', 'push', tag_remote])
        except Exception as error:
            print(str(error))
            print("Something went wrong, aborting.")

        finally:
            print('Logging out of the docker registry')
            run_with_output(['docker', 'logout', proxy_endpoint])
            os.chdir(this_dir)

    def update_service(self, session_token, service_name, service_definition):
        """Updates a service to use the given service definition

        The service_definition parameter must be a Python dict with the
        following elements:
            - "container-tag" (string): The Docker image tag to use
            - "memory-reservation" (int): Amount of memory to be reserved for
              the service
            - "memory-limit" (int): Memory limit, the service is killed and
              restarted when trying to allocate more
            - "container-port" (int): The port the service listens to for
              incoming connections
            - "environment" (list): List of dicts with "name"-"value" pairs of
              environment variables to be given to the service
        """
        this_url = os.path.join(self.url, 'services/{}'.format(service_name))
        assert("container-tag" in service_definition)
        assert("memory-reservation" in service_definition)
        assert("memory-limit" in service_definition)
        assert("container-port" in service_definition)
        assert("environment" in service_definition)
        assert(type(service_definition['environment']) is list)

        r = requests.put(
            this_url,
            headers=self._make_auth_header(session_token),
            json=service_definition
        )
        return r.json()

    def delete_service(self, session_token, service_name):
        """Stops and deletes a service and all associated resources"""
        this_url = os.path.join(self.url, 'services/{}'.format(service_name))
        r = requests.delete(
            this_url,
            headers=self._make_auth_header(session_token),
        )
        return r.json()


def run_with_output(command):
    """Runs a command and prints its output.
    Arguments:
        command {list} -- command and arguments for subprocess.run()
    """
    popen = Popen(command, stdout=PIPE, universal_newlines=True)
    for line in popen.stdout:
        print(line, end='')
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)
