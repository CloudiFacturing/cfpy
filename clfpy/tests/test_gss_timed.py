"""Tests the upload time for GSS"""
import os
import time
from contextlib import contextmanager

import clfpy as cf

gss_url = "https://api.hetcomp.org/gss-0.1/FileUtilities?wsdl"

try:
    session_token = os.environ['CFG_TOKEN']
except KeyError:
    print("CFG_TOKEN environment variable must be defined.")
    exit(-1)


@contextmanager
def timeit_context(name):
    """Context manager to time the execution of single function calls"""
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    print('[{}] finished in {} ms'.format(name, int(elapsed_time * 1000)))


def timed_upload_and_download(tk, filename, gss_ID):
    print("Starting timed upload")
    with timeit_context("Upload {}".format(filename)):
        try:
            gss_ID = gss.upload(gss_ID, tk, filename)
        except AttributeError:
            print("Attribute error, trying update instead of upload")
            gss_ID = gss.update(gss_ID, tk, filename)

    print("Starting timed download")
    while True:
        try:
            with timeit_context("Upload {}".format(filename)):
                gss.download_to_file(gss_ID, tk, filename + '.bak')
            break
        except AttributeError:
            print("Attribute error, retrying")
            continue

    # Cleanup
    os.remove(filename + '.bak')
    gss.delete(gss_ID, tk)


def create_random_file(filepath, size):
    with open(filepath, 'wb') as fout:
        fout.write(os.urandom(size))


gss = cf.GssClient(gss_url)

file_sizes = [1, 5, 10, 20, 50]
filepath = "/tmp/tempfile.bin"

for file_size in file_sizes:

    print('\n### Testing with file size {} MB'.format(file_size))

    print('Creating random file')
    create_random_file(filepath, 1024*1024*file_size)

    print('Test 1: Anselm cluster')
    gss_ID = "it4i_anselm://home/temp.bin"
    timed_upload_and_download(session_token, filepath, gss_ID)

    print('Test 2: Salomon cluster')
    gss_ID = "it4i_salomon://home/temp.bin"
    timed_upload_and_download(session_token, filepath, gss_ID)
