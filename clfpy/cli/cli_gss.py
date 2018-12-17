import sys
sys.path.append("../..")

import cmd
import readline
import os
import getpass

import clfpy as cf

AUTH_endpoint = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
GSS_endpoint = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

GSS_roots = [
        "it4i_anselm://",
        "it4i_salomon://"
]

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return the answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class GssCLI(cmd.Cmd):

    def __init__(self, token=None):
        super(GssCLI, self).__init__()
        if token is not None:
            self.session_token = token
        else:
            auth = cf.AuthClient(AUTH_endpoint)
            if "CFG_TOKEN" in os.environ:
                print("Found environment variable 'CFG_TOKEN'")
                self.session_token = os.environ["CFG_TOKEN"]
            else:
                self.session_token = self.authenticate(auth)

        self.user = auth.get_username(self.session_token)
        self.project = auth.get_project(self.session_token)

    def authenticate(self, auth):
        try:
            username = os.environ['CFG_USERNAME']
            password = os.environ['CFG_PASSWORD']
            project = os.environ['CFG_PROJECT']
            print("Found environment variables for username, password, and token")
        except KeyError:
            username = input("Please enter username: ")
            project = input("Please enter project: ")
            password = getpass.getpass("Please enter password: ")

        print("Logging in ...")
        session_token = auth.get_session_token(username, project, password)
        if "401" in str(session_token):
            print("Error: Authentication failed")
            exit()
        return session_token

    def preloop(self):
        self.gss = cf.GssClient(GSS_endpoint)
        self.root = GSS_roots[0]
        self.folder = '.'
        self.update_prompt()

        self.intro = 'Welcome to the CloudFlow command line client.'

    def get_current_path_URI(self):
        """Return current path URI."""
        if self.folder == '.':
            return self.root
        else:
            return f"{self.root}{self.folder}"

    def update_prompt(self):
        self.prompt = f"\n{self.user}@{self.project}: {self.get_current_path_URI()}$ "

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
            folders = [x['visualName'] for x in contents if x['type'] == 'FOLDER']
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
            print("Folder upload not available")
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
            print("Folder download not available")
        else:
            print(f"Error: URI {URI} not found.")


if __name__ == '__main__':
    GssCLI().cmdloop()
