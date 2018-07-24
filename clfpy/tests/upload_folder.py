#!/usr/bin/env python3

"""
Script for uploading an entire folder

Usage: update_folder FOLDER DESTINATION

  FOLDER       the folder to be uploaded, absolute or relative path
  DESTINATION  the gss destination, which must exist before
               (e.g. it4i_salomon://destination/path/)

  username, project and password must be specified in environment variables
    CFG_USERNAME, CFG_PASSWORD, CFG_PROJECT

"""

import os
import os.path
import sys
import clfpy as cf

auth_url = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
gss_url = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

def main():

    if not os.path.isdir(os.path.abspath(sys.argv[1])):
        print("Folder {} does not exists.".format(sys.argv[1]))
        return

    try:
        username = os.environ['CFG_USERNAME']
        password = os.environ['CFG_PASSWORD']
        project = os.environ['CFG_PROJECT']
    except KeyError:
        print("CFG_USERNAME, CFG_PASSWORD and CFG_PROJECT environment variables \
are not defined.")
        username = input("Please enter the username: ")
        password = input("Please enter the password: ")
        project = input("Please enter the project: ")

    print("Obtaining session token ...")
    auth = cf.AuthClient(auth_url)
    session_token = auth.get_session_token(username, project, password)
    if "Server raised fault" in str(auth.get_token_info(session_token)):
        print("Autentication failed")
        return
    print("Autentication complete")

    gss = cf.GssClient(gss_url)
    gss.upload_folder(sys.argv[2], session_token, sys.argv[1])

if __name__ == "__main__":
    main()
