"""Ugly but working hard-coded test script for the HPC client"""
import os
import filecmp
import json

import clfpy as cf

auth_url = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
hpc_url = "https://api.hetcomp.org/hpc_anselm/Images?wsdl"
gss_url = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"
username = "???"
project = 'cloudifacturing'
password = "???"

print("Obtaining session token ...")
auth = cf.AuthClient(auth_url)
session_token = auth.get_session_token(username, project, password)

hpc = cf.HpcImagesClient(hpc_url)

print("Obtaining list of registered images")
images = hpc.list_images(session_token)
print(images)

print("Uploading and registering a new image")
# 1: Create a random file
image_filepath = '/tmp/temp_image.simg'
with open(image_filepath, 'wb') as fout:
    fout.write(os.urandom(1024))

# 2: Upload the file to GSS
gss = cf.GssClient(gss_url)
gss_ID = "it4i_anselm://home/temp_image.simg"
print(gss.upload(gss_ID, session_token, image_filepath))

# 3: Register the image
print(hpc.register_image(session_token, 'temp_image.simg', gss_ID))

print("Check if new image is there")
print(hpc.get_image_info(session_token, 'temp_image.simg'))

print("Update image")
print(hpc.update_image(session_token, 'temp_image.simg', gss_ID))

print("Delete image")
print(hpc.delete_image(session_token, 'temp_image.simg'))

# Remove image from GSS
print(gss.delete(gss_ID, session_token))