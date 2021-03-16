# -*- coding: future_fstrings -*-
import cmd
import readline
import os

import clfpy as cf
from .cli_images import ImagesCLI
from .tools import query_yes_no

GSS_endpoint = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

GSS_roots = [
        "it4i_barbora://"
]


class GssCLI(cmd.Cmd, object):

    def __init__(self, token, user, project):
        super(GssCLI, self).__init__()
        self.session_token = token
        self.user = user
        self.project = project

    def preloop(self):
        self.gss = cf.GssClient(GSS_endpoint)
        self.root = GSS_roots[0]
        self.folder = '.'
        self.update_prompt()

        self.intro = ("This is the CloudFlow GSS client. "
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

    def get_current_path_URI(self):
        """Return current path URI."""
        if self.folder == '.':
            return self.root
        else:
            return f"{self.root}{self.folder}"

    def update_prompt(self):
        self.prompt = (f"\n{self.user}@{self.project} – GSS: "
                       f"{self.get_current_path_URI()}$ ")

    def make_path_URI(self, rel_path):
        new_path = os.path.normpath(os.path.join(self.folder, rel_path))
        if new_path.startswith('..'):
            raise ValueError("Path not allowed")
        elif new_path.startswith('/'):
            new_path = new_path[1:len(new_path)]
            return os.path.join(self.root, new_path), new_path
        else:
            return os.path.join(self.root, new_path), new_path

    def isfile(self, URI):
        resinfo = self.gss.get_resource_information(URI, self.session_token)
        return resinfo.type == "FILE"

    def isfolder(self, URI):
        resinfo = self.gss.get_resource_information(URI, self.session_token)
        return resinfo.type == "FOLDER"

    def exists(self, URI):
        return self.gss.contains_file(URI, self.session_token)

    def get_type(self, URI):
        resinfo = self.gss.get_resource_information(URI, self.session_token)
        return resinfo.type

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

    def do_set_storage(self, storage):
        """Change the current storage resource. Usage: set_storage STORAGE"""
        if storage in GSS_roots:
            self.root = storage
            self.update_prompt()
        else:
            print(f"Error: Unknown storage resource '{storage}'")

    def do_list_storages(self, arg):
        """List available storage locations. Usage: list_storages"""
        print(f"Available storages: {GSS_roots}")

    def do_ls(self, rel_path):
        """List folder contents. Usage: ls [FOLDER]"""
        try:
            URI, _ = self.make_path_URI(rel_path)
        except ValueError:
            print("Error: Illegal path")
            return

        resinfo = self.gss.get_resource_information(URI, self.session_token)
        if resinfo.type == "FOLDER":
            contents = self.gss.list_files_minimal(URI, self.session_token)
            folders = [x['visualName'] for x in contents
                       if x['type'] == 'FOLDER']
            files = [x['visualName'] for x in contents if x['type'] == 'FILE']
            for fol in sorted(folders):
                print(F'  {fol:<30} FOLDER')
            for fil in sorted(files):
                print(F'  {fil:<30} FILE')
        elif resinfo.type == "NOTEXIST":
            print("Error: Folder does not exist")
        else:
            print("Error: Given path is not a folder")

    def do_dir(self, rel_path):
        """List folder contents. Usage: dir [FOLDER]"""
        self.do_ls(rel_path)

    def do_cd(self, rel_path):
        """Change current folder. Usage: cd FOLDER"""
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Error: Illegal path")
            return

        if self.isfolder(URI):
            self.folder = path
            self.update_prompt()
        else:
            print("Error: Given path is not a folder")

    def do_mkdir(self, rel_path):
        """Creates a new folder relative to the current folder.
        Usage: mkdir REL_PATH
        """
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Error: Illegal path")
            return

        # Make sure the parent folder exists
        try:
            parent_URI, _ = self.make_path_URI(os.path.join(rel_path, '..'))
        except ValueError:
            print("Error: Parent folder must exist")
            return
        if not self.isfolder(parent_URI):
            print("Error: Parent folder must exist")
            return

        if not self.exists(URI):
            self.gss.create_folder(URI, self.session_token)
        else:
            print("Error: Given path already exists")

    def do_rm(self, rel_path):
        """Deletes a file or folder. Usage: rm REL_PATH"""
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Error: Illegal path")
            return

        resinfo = self.gss.get_resource_information(URI, self.session_token)
        if resinfo.type == "NOTEXIST":
            print("Error: Path doesn't exist")
            return

        if resinfo.type == "FOLDER":
            self.gss.delete_folder(URI, self.session_token)
            print(f"Removed folder {URI}")
            if path == self.folder:
                self.do_cd('..')

        elif resinfo.type == "FILE":
            print(f"Removed file {URI}")
            self.gss.delete(URI, self.session_token)

    def do_ul(self, args):
        """Upload a file or folder. Usage: ul LOCAL_PATH [REMOTE_FILENAME]"""
        arglist = args.split()
        if len(arglist) == 1:
            local_path = arglist[0]
            remote_filename = os.path.basename(local_path)
        elif len(arglist) == 2:
            local_path = arglist[0]
            remote_filename = arglist[1]
        else:
            print("Error: Too many arguments.")
            return

        if os.path.isfile(local_path):
            URI, path = self.make_path_URI(remote_filename)
            URI_type = self.get_type(URI)
            if URI_type == "FOLDER":
                print(f"Error: Folder {URI} exists")
                return
            elif URI_type == "FILE":
                overwrite = query_yes_no(f"Warning: File {URI} exists, "
                                         "do you want to overwrite?", "yes")
                if overwrite:
                    self.gss.update(URI, self.session_token, local_path)
                else:
                    print("Upload cancelled")
            else:
                print(f"Uploading new file to {URI}")
                self.gss.upload(URI, self.session_token, local_path)

        elif os.path.isdir(local_path):
            remote_filename = os.path.basename(local_path)
            URI, path = self.make_path_URI(remote_filename)
            URI_type = self.get_type(URI)
            if URI_type == "FOLDER":
                print(f"Error: Folder {URI} exists")
                return
            elif URI_type == "FILE":
                print(f"Error: File {URI} exists")
                return
            else:
                parent_URI = os.path.dirname(URI)
                print("Warning: Folder upload is not a core GSS feature. "
                      "Use at your own risk.")
                print(f"Uploading folder {local_path} to {URI} "
                      "(REMOTE_FILENAME is ignored here)")
                self.gss.upload_folder(parent_URI, self.session_token,
                                       local_path)
        else:
            print(F'Local file or folder {local_path} not found.')

    def do_dl(self, args):
        """Download a file or folder. Usage: dl REMOTE_NAME [LOCAL_PATH]"""
        arglist = args.split()
        if len(arglist) == 1:
            remote_filename = arglist[0]
            local_path = os.path.basename(remote_filename)
        elif len(arglist) == 2:
            remote_filename = arglist[0]
            local_path = arglist[1]
        else:
            print("Error: Too many arguments.")
            return

        try:
            URI, path = self.make_path_URI(remote_filename)
        except ValueError:
            print("Error: Illegal path")
            return

        URI_type = self.get_type(URI)

        if URI_type == "FILE":
            print(f"Downloading {URI} to {local_path}")
            self.gss.download_to_file(URI, self.session_token, local_path)
        elif URI_type == "FOLDER":
            print("Warning: Folder download is not a core GSS feature. "
                  "Use at your own risk")
            print(f"Downloading folder {URI} (LOCAL_PATH is ignored here)")
            self.gss.download_folder(URI, self.session_token)
        else:
            print(f"Error: URI {URI} not found.")

    def do_img_ls(self, arg):
        """List Singularity images registered on the current cluster. Usage: img_ls"""
        img = ImagesCLI(self.session_token, self.user, self.project, self.root)
        img.do_ls(arg)

    def do_img_register(self, arg):
        """Registers a file from the current folder as a Singularity image. Usage: img_register FILENAME"""
        if arg == "":
            print("Error: File name must be given")
            return
        if len(arg.split()) > 1:
            print("Error: Too many arguments")
            return

        rel_path = arg
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Error: Illegal path")
            return

        resinfo = self.gss.get_resource_information(URI, self.session_token)
        if not resinfo.type == "FILE":
            print("Error: File doesn't exist")
            return

        target_name = os.path.basename(path)

        img = ImagesCLI(self.session_token, self.user, self.project, self.root)
        if img.exists(target_name):
            overwrite = query_yes_no(f"Image '{target_name}' already registered. Overwrite?", "yes")
            if not overwrite:
                print("Cancelled")
                return
            img.do_update(f"{target_name} {URI}")
        else:
            img.do_register(f"{URI} {target_name}")

    def do_img_rm(self, arg):
        """Remove a Singularity images registered on the current cluster. Usage: img_rm NAME"""
        img = ImagesCLI(self.session_token, self.user, self.project, self.root)
        img.do_rm(arg)


if __name__ == '__main__':
    GssCLI().cmdloop()
