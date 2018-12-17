#!/usr/bin/env python3
"""Command-line client for CFG platform"""

import sys
sys.path.append("../..")

import os.path
import os
import getpass
import re
import subprocess
import cmd
import clfpy as cf

__author__ = "Leonardo Cosma <leonardo.cosma@cetma.it>"
__version__ = "2.0.0"

auth_url = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
gss_url = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"


class cfg_client:
    """GSS/HPC client."""

    _session_token = ""
    _gss = ""
    _hpc = ""
    _root = ""
    _folder = ""
    _roots = ["it4i_anselm://", "it4i_salomon://"]
    _hpcs = {"it4i_anselm://": "https://api.hetcomp.org/hpc-4-anselm/Images?wsdl",
             "it4i_salomon://": "https://api.hetcomp.org/hpc-4-salomon/Images?wsdl"}

    def __init__(self):
        """Initialize the client."""
        try:
            username = os.environ['CFG_USERNAME']
            password = os.environ['CFG_PASSWORD']
            project = os.environ['CFG_PROJECT']
        except KeyError:
            print("CFG_USERNAME, CFG_PASSWORD and CFG_PROJECT environment variables \
            are not defined.")
            username = input("Please enter the username: ")
            password = getpass.getpass("Please enter the password: ")
            project = input("Please enter the project: ")
        self._user = username
        self._project = project
        auth = cf.AuthClient(auth_url)
        self._session_token = auth.get_session_token(username, project, password)
        if "Server raised fault" in str(auth.get_token_info(self._session_token)):
            print("Authentication failed")
            exit()
        self._gss = cf.GssClient(gss_url)
        self._root = "it4i_anselm://"
        self._folder = "home"
        self._hpc = cf.HpcImagesClient(self._hpcs[self._root])
        return

    def _verify(self, path):
        return self._gss.contains_file(path, self._session_token)

    def _isfile(self, path):
        type = self._gss.get_resource_information(path, self._session_token)['type'].lower()
        return type == "file"

    def _isfolder(self, path):
        type = self._gss.get_resource_information(path, self._session_token)['type'].lower()
        return type == "folder"

    def _path(self, folder):
        """Given a path, return the complete path."""
        current_path = self._root + self._folder
        if folder == "..":
            return os.path.dirname(current_path)  # parent folder
        elif folder == "" or folder is None:
            return current_path  # this folder
        elif re.compile(r'^\S+://\S+').match(folder):
            return folder  # full path WITH root
        elif folder[0] == "/":
            return self._root + folder  # full path WITHOUT root
        else:
            return current_path + "/" + folder  # subfolder

    def _remove_root(self, path):
        return re.sub(r'^\S+://', '', path)

    def _upload_file(self, uri):
        path = self._path(self._folder + "/" + os.path.basename(uri))
        if self._verify(path):
            if self._isfolder(path):
                print(F'Folder {os.path.basename(uri)} already exists.')
            else:
                self._gss.update(path, self._session_token, uri)
                print(F'File {os.path.basename(uri)} updated.')
        else:
            self._gss.upload(path, self._session_token, uri)
            print(F'File {os.path.basename(uri)} uploaded.')
        return

    def _upload_folder(self, uri):
        path = self._path(self._folder + "/" + os.path.basename(uri))
        ppath = os.path.dirname(path)
        if self._verify(path):
            print(F'Remote file or folder {os.path.basename(uri)} already exists.')
        else:
            self._gss.upload_folder(ppath, self._session_token, uri)
            print(F'Folder {os.path.basename(uri)} uploaded.')
        return

    def get_current_path_URI(self):
        """Return current path URI."""
        return f"{self._root}{self._folder}"

    def cdir(self, folder):
        """Change current folder."""
        path = self._path(folder)
        if self._verify(path) and self._isfolder(path):
            self._folder = self._remove_root(path)
        else:
            print(F'Folder {self._remove_root(path)} not found.')
        return

    def croot(self, root):
        """Change current remote resource."""
        if root in self._roots:
            self._root = root
            self._folder = "/home"
            self._hpc = cf.HpcImagesClient(self._hpcs[self._root])
        else:
            print(F'Remote resource {root} not found.')
        return

    def list(self, folder):
        """List the content of a folder."""
        path = self._path(folder)
        if self._verify(path) and self._isfolder(path):
            entry_list = [x for x in self._gss.list_files_minimal(path, self._session_token)]
            folders = [x['visualName'] for x in entry_list if x['type'] == 'FOLDER']
            files = [x['visualName'] for x in entry_list if x['type'] == 'FILE']
            for fol in sorted(folders):
                print(F'  {fol:<30} FOLDER')
            for fil in sorted(files):
                print(F'  {fil:<30} FILE')
        else:
            print(F'Folder {self._remove_root(path)} not found.')
        return

    def cat(self, file):
        """Display the content of a file."""
        path = self._path(file)
        if not self._verify(path):
            print(F'File {self._remove_root(path)} not found.')
            return
        if not self._isfile(path):
            print(F'{self._remove_root(path)} is a folder.')
            return
        self._gss.download_to_file(path, self._session_token, 'temp')
        for line in open('temp', 'r'):
            print(line, end='')
        os.remove('temp')
        return

    def mkdir(self, folder):
        """Create a folder."""
        path = self._path(folder)
        parent_path = os.path.dirname(path)
        if self._verify(path):
            print(F'Folder {self._remove_root(path)} already exists.')
        else:
            if self._verify(parent_path) and self._isfolder(parent_path):
                self._gss.create_folder(path, self._session_token)
            else:
                print(F'Parent folder {self._remove_root(parent_path)} not found.')
        return

    def delete(self, uri):
        """Delete a folder or a file."""
        path = self._path(uri)
        if self._verify(path) and self._isfolder(path):
            if self._remove_root(path) not in ["/home", "/scratch"]:
                self._gss.delete_folder(path, self._session_token)
                print(F'Folder {self._remove_root(path)} deleted.')
            if self._remove_root(path) == self._folder:
                self._folder = os.path.dirname(self._remove_root(path))
        elif self._verify(path) and self._isfile(path):
            self._gss.delete(path, self._session_token)
            print(F'File {self._remove_root(path)} deleted.')
        else:
            print(F'File or folder {self._remove_root(path)} not found.')
        return

    def upload(self, uri):
        """Upload a folder or a file."""
        if os.path.isfile(uri):
            self._upload_file(uri)
        elif os.path.isdir(uri):
            self._upload_folder(uri)
        else:
            print(F'Local file or folder {uri} not found.')
        return

    def download(self, uri):
        """Download a folder or a file."""
        path = self._path(uri)
        if self._verify(path):
            if self._isfile(path):
                self._gss.download_to_file(path, self._session_token, os.path.basename(uri))
                print(F'File {os.path.basename(uri)} downloded.')
            else:
                self._gss.download_folder(path, self._session_token)
                print(F'Folder {os.path.basename(uri)} downloded.')
        else:
            print(F'File or folder {self._remove_root(path)} not found.')
        return

    def img_register(self, image, name):
        """Register an image."""
        path = self._path(image)
        if not self._verify(path):
            print(F'Image file {os.path.basename(image)} not found.')
            return
        img_list = [x['name'] for x in self._hpc.list_images(self._session_token)]
        if name in img_list:
            print(F'An image with name {name} is already registered.')
            return
        try:
            self._hpc.register_image(self._session_token, name, path)
        except:
            print("Maybe a timeout error occured, but the image has been registered.")
            print("Check via img_list command.")
        return

    def img_list(self):
        """List the registered images."""
        img_list = [x['name'] for x in self._hpc.list_images(self._session_token)]
        print(F'Images registered in {self._root}')
        for img in img_list:
            print(F'    {img}')
        return

    def img_delete(self, name):
        """Unregister an image."""
        img_list = [x['name'] for x in self._hpc.list_images(self._session_token)]
        if name not in img_list:
            print(F'Image with name {name} not found.')
            return
        self._hpc.delete_image(self._session_token, name)
        return


class CmdLine(cmd.Cmd):
    """Class to handle command line interface."""

    def preloop(self):
        self.intro = 'Welcome to CFG command line client.'
        self.file = None
        self.client = cfg_client()
        self.update_prompt()

    def update_prompt(self):
        self.prompt = f"{self.client._user}@{self.client._project}: {self.client.get_current_path_URI()}$ "

    def do_cd(self, arg):
        """Change current folder. Usage: cd FOLDER"""
        self.client.cdir(arg)
        self.update_prompt()
        return

    def do_croot(self, arg):
        """Change the current remote resource. Usage: croot RESOURCE"""
        self.client.croot(arg)
        self.update_prompt()
        return

    def do_list(self, arg):
        """List the content of a folder. Usage: list FOLDER"""
        self.client.list(arg)

    def do_ls(self, arg):
        """List the content of a folder. Usage: ls FOLDER"""
        self.client.list(arg)

    def do_dir(self, arg):
        """List the content of a folder. Usage: dir FOLDER"""
        self.client.list(arg)

    def do_cat(self, arg):
        """List the content of a file. Usage: cat FILE"""
        self.client.cat(arg)

    def do_mkdir(self, arg):
        """Create a folder. Usage: mkdir FOLDER"""
        self.client.mkdir(arg)

    def do_del(self, arg):
        """Create a resource. Usage: del RES"""
        self.client.delete(arg)
        self.update_prompt()

    def do_up(self, arg):
        """Upload a resource. Usage: up RES"""
        self.client.upload(arg)

    def do_down(self, arg):
        """Download a resource. Usage: down RES"""
        self.client.download(arg)

    def do_img_reg(self, arg):
        """Register an image. Usage: img_reg PATH NAME"""
        if len(arg.split()) == 2:
            self.client.img_register(arg.split()[0], arg.split()[1])

    def do_img_list(self, arg):
        """List registered images. Usage: img_list"""
        self.client.img_list()

    def do_img_del(self, arg):
        """Unregister an image. Usage: img_del NAME"""
        self.client.img_delete(arg)

    def do_clear(self, arg):
        """Clear the screen."""
        subprocess.run('clear', shell=True)

    def do_shell(self, arg):
        """Execute shell command. Usage shell CMD"""
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
    CmdLine().cmdloop()
