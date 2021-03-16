# -*- coding: future_fstrings -*-
import cmd
import readline
import os

import clfpy as cf
from .tools import query_yes_no

IMG_endpoints = {
        "it4i_barbora://": "https://api.hetcomp.org/hpc-4-barbora/Images?wsdl"
}


class ImagesCLI(cmd.Cmd, object):

    def __init__(self, token, user, project, root="it4i_barbora://"):
        super(ImagesCLI, self).__init__()
        self.session_token = token
        self.user = user
        self.project = project
        self.root = root
        self.img = cf.HpcImagesClient(IMG_endpoints[self.root])

    def preloop(self):
        self.image_list = []
        self.make_image_list()
        self.update_prompt()
        self.intro = ("This is the CloudFlow Images client. "
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
        self.prompt = (f"\n{self.user}@{self.project} – IMAGES: {self.root}$ ")

    def name_completion(self, text, line, begidx, endidx):
        matches = [n for n in self.image_names if n.startswith(text)]
        if len(matches) == 1:
            matches[0] += ' '
        return matches

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

    def do_set_cluster(self, cluster):
        """Change the current cluster. Usage: set_cluster CLUSTER"""
        if len(cluster.split()) > 1:
            print("Error: Too many arguments")
            return
        if cluster == "":
            print("Error: No cluster name given")
            return
        if cluster in IMG_endpoints:
            self.root = cluster
            self.img = cf.HpcImagesClient(IMG_endpoints[self.root])
            self.update_prompt()
        else:
            print(f"Error: Unknown cluster '{cluster}'")

    def complete_set_cluster(self, text, line, begidx, endidx):
        matches = [c for c in IMG_endpoints.keys() if c.startswith(text)]
        if len(matches) == 1:
            matches[0] += ' '
        return matches

    def do_list_clusters(self, arg):
        """List available clusters. Usage: list_clusters"""
        print(f"Available clusters: {list(IMG_endpoints.keys())}")

    def make_image_list(self):
        self.image_list = self.img.list_images(self.session_token)
        self.image_names = [n['name'] for n in self.image_list]

    def do_ls(self, arg):
        """List registered images. Usage: ls"""
        if arg != "":
            print("Error: Too many arguments")
            return

        self.make_image_list()
        print(f"{'Image name':<40}{'Size':<15}{'Last modified'}")
        print(f"{'==========':<40}{'====':<15}{'============='}")
        for i in self.image_list:
            print(f"{i['name']:<40}{i['size']:<15}{i['lastModified']}")

    def exists(self, name):
        try:
            self.img.get_image_info(self.session_token, name)
        except (cf.ImageNotFoundException, cf.ImageNameIllegalException):
            return False
        return True

    def do_register(self, arg):
        """Registers a GSS URI as a new image. Usage: register GSS_URI TARGET_NAME"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Wrong number of arguments")
            return
        gss_URI = args[0]
        target_name = args[1]

        if self.exists(target_name):
            print(f"Error: Image {target_name} already exists, use update method instead")
            return

        try:
            self.img.register_image(self.session_token, target_name, gss_URI)
        except cf.ImageSourceNotFoundException:
            print(f"Error: Source file {gss_URI} not found")
            return
        except cf.ImageNameIllegalException:
            print(f"Error: Target name {target_name} is illegal")
            return

        print(f"Image {target_name} registered")
        self.make_image_list()

    def do_update(self, arg):
        """Updates an existing image. Usage: update NAME GSS_URI"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Wrong number of arguments")
            return
        target_name = args[0]
        gss_URI = args[1]

        if not self.exists(target_name):
            print(f"Error: Image {target_name} doesn't exist, use register method instead")
            return

        try:
            self.img.update_image(self.session_token, target_name, gss_URI)
        except cf.ImageSourceNotFoundException:
            print(f"Error: Source file {gss_URI} not found")
            return
        except cf.ImageNameIllegalException:
            print(f"Error: Target name or source file path illegal")
            return

        print(f"Image {target_name} updated")
        self.make_image_list()

    complete_update = name_completion

    def do_rm(self, arg):
        """Removes a registered image. Usage: rm IMAGE_NAME"""
        if arg == "":
            print("Error: Must specify an image name")
            return
        if len(arg.split()) > 1:
            print("Error: Too many arguments")
            return

        name = arg
        if not self.exists(name):
            print(f"Error: Image '{name}' doesn't exist")
            return

        print(self.img.delete_image(self.session_token, name))
        self.make_image_list()

    complete_rm = name_completion


if __name__ == '__main__':
    ImagesCLI().cmdloop()
