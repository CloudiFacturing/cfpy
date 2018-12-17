import sys
sys.path.append("../..")

import cmd
import os

import clfpy as cf

AUTH_endpoint = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
GSS_endpoint = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

GSS_roots = [
        "it4i_anselm://",
        "it4i_salomon://"
]

class GssCLI(cmd.Cmd):

    def authenticate(self, auth_url):
        try:
            username = os.environ['CFG_USERNAME']
            password = os.environ['CFG_PASSWORD']
            project = os.environ['CFG_PROJECT']
        except KeyError:
            print("CFG_USERNAME, CFG_PASSWORD and CFG_PROJECT environment variables \
            are not defined.")
            username = input("Please enter username: ")
            project = input("Please enter project: ")
            password = getpass.getpass("Please enter password: ")

        self.user = username
        self.project = project
        auth = cf.AuthClient(auth_url)
        self.session_token = auth.get_session_token(username, project, password)
        if "Server raised fault" in str(auth.get_token_info(self.session_token)):
            print("Authentication failed")
            exit()

    def get_current_path_URI(self):
        """Return current path URI."""
        if self.folder == '.':
            return self.root
        else:
            return f"{self.root}{self.folder}"

    def update_prompt(self):
        self.prompt = f"\n{self.user}@{self.project}: {self.get_current_path_URI()}$ "

    def preloop(self):
        self.authenticate(AUTH_endpoint)

        self.gss = cf.GssClient(GSS_endpoint)
        self.root = GSS_roots[0]
        self.folder = '.'
        self.update_prompt()

        self.intro = 'Welcome to the CloudFlow command line client.'
        self.file = None

    def make_path_URI(self, rel_path):
        new_path = os.path.normpath(os.path.join(self.folder, rel_path))
        if new_path.startswith('..'):
            raise ValueError("Path not allowed")
        elif new_path.startswith('/'):
            new_path = new_path[1:len(new_path)]
            return os.path.join(self.root, new_path), new_path
        else:
            return os.path.join(self.root, new_path), new_path

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
            print(f"Unknown storage resource '{storage}'")

    def do_list_storages(self, arg):
        """List available storage locations. Usage: list_storages"""
        print(f"Available storages: {GSS_roots}")

    def do_ls(self, rel_path):
        """List folder contents. Usage: ls [FOLDER]"""
        try:
            URI, _ = self.make_path_URI(rel_path)
        except ValueError:
            print("Illegal path")
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
            print("Folder does not exist")
        else:
            print("Given path is not a folder")

    def do_dir(self, rel_path):
        """List folder contents. Usage: dir [FOLDER]"""
        self.do_ls(rel_path)

    def do_cd(self, rel_path):
        """Change current folder. Usage: cd FOLDER"""
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Illegal path")
            return

        resinfo = self.gss.get_resource_information(URI, self.session_token)
        if resinfo.type == "FOLDER":
            self.folder = path
            self.update_prompt()
        else:
            print("Given path is not a folder")

    def do_mkdir(self, rel_path):
        """Creates a new folder relative to the current folder.
        Usage: mkdir REL_PATH
        """
        try:
            URI, path = self.make_path_URI(rel_path)
        except ValueError:
            print("Illegal path")
            return

        resinfo = self.gss.get_resource_information(URI, self.session_token)
        if resinfo.type == "NOTEXIST":
            # TODO: Check that parent folder exists (GSS should return error!)
            self.gss.create_folder(URI, self.session_token)
        else:
            print("Given path exists, cannot re-create")



#   def do_cat(self, arg):
#       """List the content of a file. Usage: cat FILE"""
#       self.client.cat(arg)

#   def do_mkdir(self, arg):
#       """Create a folder. Usage: mkdir FOLDER"""
#       self.client.mkdir(arg)

#   def do_del(self, arg):
#       """Create a resource. Usage: del RES"""
#       self.client.delete(arg)
#       self.update_prompt()

#   def do_up(self, arg):
#       """Upload a resource. Usage: up RES"""
#       self.client.upload(arg)

#   def do_down(self, arg):
#       """Download a resource. Usage: down RES"""
#       self.client.download(arg)

#   def do_img_reg(self, arg):
#       """Register an image. Usage: img_reg PATH NAME"""
#       if len(arg.split()) == 2:
#           self.client.img_register(arg.split()[0], arg.split()[1])

#   def do_img_list(self, arg):
#       """List registered images. Usage: img_list"""
#       self.client.img_list()

#   def do_img_del(self, arg):
#       """Unregister an image. Usage: img_del NAME"""
#       self.client.img_delete(arg)

#   def do_clear(self, arg):
#       """Clear the screen."""
#       subprocess.run('clear', shell=True)

#   def do_shell(self, arg):
#       """Execute shell command. Usage shell CMD"""
#       os.system(arg)

#   def do_exit(self, arg):
#       """Exit the application."""
#       print('Goodbye')
#       return True

#   def do_EOF(self, arg):
#       """Exit the application."""
#       print('Goodbye')
#       return True

if __name__ == '__main__':
    GssCLI().cmdloop()
