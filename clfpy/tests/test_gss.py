"""Ugly but working hard-coded test script for the GSS client"""
import os
import filecmp

import clfpy as cf

auth_url = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
gss_url = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

try:
    session_token = os.environ['CFG_TOKEN']
except KeyError:
    print("CFG_TOKEN environment variable must be defined.")
    exit(-1)

print('\n### Tests on IT4I cluster storage ###')
print("Querying resource information for it4i_anselm://home ...")
gss = cf.GssClient(gss_url)
res_info = gss.get_resource_information('it4i_anselm://home', session_token)
print(res_info)

print("Listing files in it4i_anselm://home...")
print(gss.list_files_minimal('it4i_anselm://home', session_token))

print("Uploading a file ...")
try:
    gss_ID = gss.upload('it4i_anselm://home/test_gss.py',
                        session_token, 'test_gss.py')
    print("-> Uploaded file is {}".format(gss_ID))
except AttributeError:
    print("File seems to exist")
    gss_ID = 'it4i_anselm://home/test_gss.py'

print("Downloading the same file ...")
gss.download_to_file(gss_ID, session_token, 'test_gss_downloaded.py')

assert(filecmp.cmp('test_gss.py', 'test_gss_downloaded.py'))

print("Updating the file ...")
gss.update(gss_ID, session_token, 'test_gss.py')

print("Deleting uploaded file ...")
result = gss.delete(gss_ID, session_token)

print("Deleting downloaded file ...")
os.remove('./test_gss_downloaded.py')

print("\nTesting upload of an empty file")
fname = "./empty_file"
with open(fname, 'a'):
    os.utime(fname, None)
gss_ID = "it4i_anselm://home/empty_file"
print("{} existing?".format(gss_ID))
print(gss.contains_file(gss_ID, session_token))
print("Uploading")
gss.upload(gss_ID, session_token, fname)
print("{} existing?".format(gss_ID))
print(gss.contains_file(gss_ID, session_token))
print("Deleting")
result = gss.delete(gss_ID, session_token)
os.remove('./empty_file')
