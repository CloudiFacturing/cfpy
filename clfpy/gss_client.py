# -*- coding: utf-8 -*-
"""Lightweight SOAP client to communicate with GSS"""
import os
import sys
import time
import requests

from clfpy import SoapClient


class GssClient(SoapClient):
    """Lightweight GSS SOAP client

    Create by passing a WSDL URL:
        gss = GssClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(GssClient, self).__init__(wsdl_url)

    def get_resource_information(self, gss_ID, session_token):
        """Queries the resource information for a GSS ID."""
        return self.method_call('getResourceInformation',
                                [gss_ID, session_token])

    def list_files(self, gss_ID, session_token):
        """Lists contents of a folder defined by gss_ID."""
        return self.method_call('listFiles',
                                [gss_ID, session_token])

    def list_files_minimal(self, gss_ID, session_token):
        """Lists minimal contents of a folder defined by gss_ID.

        The minimal listing does not contain any request description objects.
        """
        return self.method_call('listFilesMinimal',
                                [gss_ID, session_token])

    def create_folder(self, gss_ID, session_token):
        """Creates a folder specified by gss_ID."""
        return self.method_call('createFolder',
                                [gss_ID, session_token])

    def delete_folder(self, gss_ID, session_token):
        """Deletes the folder specified by gss_ID."""
        return self.method_call('deleteFolder',
                                [gss_ID, session_token])

    def contains_file(self, gss_ID, session_token):
        """Returns true if the given GSS ID exists."""
        return self.method_call('containsFile',
                                [gss_ID, session_token])

    def get_direct_interaction_endpoint(self, gss_ID, session_token):
        """Returns the storage-solution end point the gss ID points to."""
        return self.method_call('getDirectInteractionEndpoint',
                                [gss_ID, session_token])

    def download_to_file(self, gss_ID, session_token, out_filename,
                         progress=True):
        """Downloads from a GSS ID to a file."""
        res_info = self.get_resource_information(gss_ID, session_token)
        read_desc = res_info.readDescription

        if not read_desc.supported:
            raise AttributeError('Read operation not allowed')

        headers = {h.key: h.value for h in read_desc.headers}

        method = get_reqmethod(read_desc.httpMethod)
        response = method(read_desc.url, headers=headers, stream=True)
        response_len = int(response.headers["Content-Length"])
        saved_len = 0
        start_time = time.time()
        with open(out_filename, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=256):
                out_file.write(chunk)
                saved_len += len(chunk)
                time_elapsed = time.time() - start_time
                speed = saved_len/1000/time_elapsed
                if progress:
                    print_progress(saved_len, response_len, prefix="DL:",
                                   suffix="{:.1f} kB/s".format(speed))

    def upload(self, gss_ID, session_token, in_filename, progress=True):
        """Uploads from a file to a new, nonexisting GSS ID."""
        res_info = self.get_resource_information(gss_ID, session_token)
        create_desc = res_info.createDescription

        if not create_desc.supported:
            raise AttributeError('Create operation not allowed')

        return self._create_or_update(gss_ID, session_token, in_filename,
                                      res_info, create_desc, progress)

    def update(self, gss_ID, session_token, in_filename, progress=True):
        """Updates an existing GSS ID from a file."""
        res_info = self.get_resource_information(gss_ID, session_token)
        update_desc = res_info.updateDescription

        if not update_desc.supported:
            raise AttributeError('Update operation not allowed')

        return self._create_or_update(gss_ID, session_token, in_filename,
                                      res_info, update_desc, progress)

    def _create_or_update(self, gss_ID, session_token, in_filename, res_info,
                          req_desc, progress=True):
        """Utility function for general upload"""
        headers = {h.key: h.value for h in req_desc.headers}
        file_size = os.stat(in_filename).st_size
        headers["Content-Length"] = "%d" % file_size

        # WORKAROUND!
        # The requests library cannot handle file descriptors of empty files.
        # Therefore, we replace the file descriptor with an empty string if the
        # file is empty.
        # Should be fixed in requests 3.x.x, details here:
        # https://github.com/requests/requests/issues/4215

        method = get_reqmethod(req_desc.httpMethod)
        if file_size == 0:
            response = method(req_desc.url, headers=headers, data='')
        else:
            with open(in_filename, "rb") as in_file:
                if progress:
                    data_in = ReadProgress(in_file, file_size,
                                           print_progress)
                else:
                    data_in = in_file
                response = method(req_desc.url, headers=headers, data=data_in)

        if res_info.queryForName:
            return response.headers["filename"]
        else:
            return gss_ID

    def delete(self, gss_ID, session_token):
        """Deletes a file or folder specified by gss_ID."""
        res_info = self.get_resource_information(gss_ID, session_token)
        delete_desc = res_info.deleteDescription

        if not delete_desc.supported:
            raise AttributeError('Delete operation not allowed')

        headers = {h.key: h.value for h in delete_desc.headers}

        method = get_reqmethod(delete_desc.httpMethod)
        response = method(delete_desc.url, headers=headers)

        return response.text

    def _scan_gss_folder(self, gss_path, session_token):
        """ Scans a GSS folder returning lists of its files and sub-folders"""
        subfolders = []
        files = []
        content = self.list_files_minimal(gss_path, session_token)
        for c in content:
            if 'FOLDER' in c['type']:
                subfolders.append(c['uniqueName'])
            if 'FILE' in c['type']:
                files.append(c['uniqueName'])
        return subfolders, files

    def _scan_gss_tree(self, gss_tree, session_token):
        """ Scans recursively a GSS tree returning lists of all its files and sub-folders"""
        gss_dirlist= [gss_tree]
        gss_filelist = []
        scanned_folders = 0
        while scanned_folders is not len(gss_dirlist):
            for i in range(scanned_folders, len(gss_dirlist)):
                print("Scanning {}...".format(gss_dirlist[i]))
                subfolders, contained_files = self._scan_gss_folder(gss_dirlist[i], session_token)
                gss_dirlist.extend(subfolders)
                gss_filelist.extend(contained_files)
                scanned_folders += 1
        return gss_dirlist, gss_filelist

    def download_folder(self, gss_tree,session_token, in_foldername="."):
        """ Downloads from a GSS tree to a folder """
        gss_dirlist, gss_filelist = self._scan_gss_tree(gss_tree, session_token)
        gss_base=""
        for l in gss_tree.split(sep="/")[:-1]:
            gss_base += l
            gss_base += "/"
        local_base = os.path.abspath(in_foldername) + "/"
        dirlist =  [d.replace(gss_base,local_base) for d in gss_dirlist]
        filedict = { f : f.replace(gss_base,local_base) for f in gss_filelist}
        print("Creating local folders...")
        try:
            for d in dirlist:
                print("Creating folder {}".format(d))
                os.mkdir(d)
            print("Downloading files...")
            for gss_file, local_file in filedict.items():
                print(local_file)
                self.download_to_file(gss_file, session_token, local_file)
        except FileExistsError:
                print("Local file or folder already exists")
        return

    def upload_folder(self, gss_tree, session_token, in_foldername):
        """ Uploads from a local folder to a new, nonexisting GSS ID. """
        dirlist = [os.path.join(root,dir) for root,dirs,__ in os.walk(os.path.abspath(in_foldername))
                for dir in dirs]
        filelist = [os.path.join(root,file) for root,__,files in os.walk(os.path.abspath(in_foldername))
                for file in files]
        dirlist.append(os.path.abspath(in_foldername))
        local_base = ""
        for l in os.path.abspath(in_foldername).split(sep="/")[:-1]:
            local_base += l
            local_base += "/"
        gss_base = gss_tree
        if gss_base[-1] is not "/":
            gss_base += "/"
        gss_dirlist =  [d.replace(local_base,gss_base) for d in dirlist]
        gss_filedict = { f : f.replace(local_base,gss_base) for f in filelist}
        gss_dirlist.sort()
        print("Creating remote folders...")
        for gss_dir in gss_dirlist:
            self.create_folder(gss_dir, session_token)
        print("Uploading files...")
        for local_file, gss_file in gss_filedict.items():
            print(self.upload(gss_file, session_token, local_file))
        return

def get_reqmethod(http_method):
    return getattr(requests, http_method.lower())


def print_progress(iteration, total, prefix='', suffix=''):
    """
    Call in a loop to create terminal progress bar

    Adapted from:
    https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a#file-print_progress-py

    Args:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
    """
    decimals = 1
    bar_length = 100
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%',
        suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


class ReadProgress(object):
    """File-like object with a progress bar for read operations"""

    def __init__(self, flo, flo_size, callback):
        self._len = flo_size
        self._read_len = 0
        self._io = flo
        self._callback = callback
        self._start_time = time.time()

    def __len__(self):
        return self._len

    def read(self, *args):
        chunk = self._io.read(*args)
        if len(chunk) > 0:
            self._read_len += len(chunk)
            time_elapsed = time.time() - self._start_time
            speed = self._read_len/1000/time_elapsed
            print_progress(self._read_len, self._len, prefix="UL:",
                           suffix="{:.1f} kB/s".format(speed))
        return chunk
