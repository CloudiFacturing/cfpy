"""Ugly but working hard-coded test script for the AuthManager client"""
from contextlib import contextmanager
import time
import cfpy

auth_url = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
username = "???"
project = 'cloudifacturing'
password = "???"

@contextmanager
def timeit_context(name):
    """Context manager to time the execution of single function calls"""
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    print('[{}] finished in {} ms'.format(name, int(elapsed_time * 1000)))


def main():
    auth = cfpy.AuthClient(auth_url, )
    with timeit_context("get_session_token"):
        session_token = auth.get_session_token(username, project, password)

    with timeit_context("get_token_info"):
        auth.get_token_info(session_token)
    with timeit_context("get_token_info_complete"):
        auth.get_token_info_complete(session_token)
    with timeit_context("validate_session_token (valid token)"):
        print(auth.validate_session_token(session_token))
    with timeit_context("validate_session_token (invalid token)"):
        print(auth.validate_session_token(session_token+'bla'))
    with timeit_context("get_username"):
        print(auth.get_username(session_token))
    with timeit_context("get_project"):
        print(auth.get_project(session_token))
    with timeit_context("get_roles"):
        print(auth.get_roles(session_token))
    with timeit_context("get_email"):
        print(auth.get_email(session_token))

    with timeit_context("get_endpoint"):
        print(auth.get_endpoint(session_token, 'swift'))
    with timeit_context("get_openstack_token"):
        print(auth.get_openstack_token(session_token))


if __name__ == "__main__":
    main()
