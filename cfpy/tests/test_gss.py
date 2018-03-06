"""Ugly but working hard-coded test script for the GSS client"""
import os

import cfpy as cf

auth_url = "https://caxman.clesgo.net/sintef/auth/authManager/AuthManager?wsdl"
gss_url = "https://caxman.clesgo.net/sintef/infrastructure/gss-0.1/FileUtilities?wsdl"
username = ???
project = 'caxman'
password = ???

print("Obtaining session token ...")
auth = cf.AuthClient(auth_url)
session_token = auth.get_session_token(username, project, password)

print("Querying resource information for swift://caxman/sintef ...")
gss = cf.GssClient(gss_url)
res_info = gss.get_resource_information('swift://caxman/sintef', session_token)
print(res_info)

print("Listing files in swift://caxman/sintef ...")
print(gss.list_files_minimal('swift://caxman/sintef/robert', session_token))

print("Uploading a file ...")
try:
    gss_ID = gss.upload('swift://caxman/sintef/robert/test_gss.py',
                        session_token, 'test_gss.py')
    print("-> Uploaded file is {}".format(gss_ID))
except AttributeError:
    print("File seems to exist")

print("Downloading the same file ...")
gss.download_to_file('swift://caxman/sintef/robert/test_gss.py',
                              session_token, 'test_gss_downloaded.py')

print("Updating the file ...")
gss.update('swift://caxman/sintef/robert/test_gss.py', session_token,
           'test_gss.py')

print("Deleting uploaded file ...")
result = gss.delete('swift://caxman/sintef/robert/test_gss.py', session_token)

print("Deleting downloaded file ...")
os.remove('./test_gss_downloaded.py')
