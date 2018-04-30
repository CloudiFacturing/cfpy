"""Lightweight SOAP client to communicate with the authentication manager"""
from clfpy import SoapClient


class AuthClient(SoapClient):
    """Lightweight AuthManager SOAP client

    Create by passing a WSDL URL:
        auth = AuthClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(AuthClient, self).__init__(wsdl_url)

    def get_session_token(self, username, project, password):
        return self.method_call('getSessionToken', [username, password,
                                                    project])

    def get_token_info(self, session_token):
        return self.method_call('getTokenInfo', [session_token])

    def get_token_info_complete(self, session_token):
        return self.method_call('getTokenInfoComplete', [session_token])

    def validate_session_token(self, session_token):
        return self.method_call('validateSessionToken', [session_token])

    def get_username(self, session_token):
        return self.method_call('getUsername', [session_token])

    def get_project(self, session_token):
        return self.method_call('getProject', [session_token])

    def get_roles(self, session_token):
        return self.method_call('getRoles', [session_token])

    def get_email(self, session_token):
        return self.method_call('getEmail', [session_token])

    def get_endpoint(self, session_token, component):
        return self.method_call('getEndpoint', [session_token, component])

    def get_openstack_token(self, session_token):
        return self.method_call('getOpenStackToken', [session_token])

    def count_workflows(self):
        return self.method_call('countWorkflows', [])


class AuthUsersClient(SoapClient):
    """Lightweight AuthManager/Users SOAP client

    Create by passing a WSDL URL:
        auth_users = AuthUsersClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(AuthUsersClient, self).__init__(wsdl_url)

    def create_user(self, token, username, password, email, description,
                    project_ID):
        return self.method_call('createUser', [token, username, password,
                                               email, description, project_ID])

    def delete_user(self, token, user_ID):
        return self.method_call('deleteUser', [token, user_ID])

    def deactivate_user(self, token, user_ID):
        return self.method_call('deactivateUser', [token, user_ID])

    def add_user_to_project(self, token, user_ID, project_ID):
        return self.method_call('addToProject', [token, user_ID, project_ID])

    def change_password(self, token, user_ID, old_password, new_password):
        return self.method_call('changePassword', [token, user_ID,
                                                   old_password, new_password])

    def reset_password(self, token, user_ID):
        return self.method_call('resetPassword', [token, user_ID])

    def update_email(self, token, new_email):
        return self.method_call('updateEmail', [token, new_email])

    def assign_role_to_user(self, token, user_ID, project_ID, rolename):
        return self.method_call('assignRole', [token, user_ID, project_ID,
                                               rolename])

    def withdraw_role_from_user(self, token, user_ID, project_ID, rolename):
        return self.method_call('withdrawRole', [token, user_ID, project_ID,
                                                 rolename])

    def list_possible_roles(self, token):
        return self.method_call('listPossibleRoles', [token])

    def list_roles_for_user_in_project(self, token, user_ID, project_ID):
        return self.method_call('listRolesForUserInProject', [token, user_ID,
                                                              project_ID])


class AuthProjectsClient(SoapClient):
    """Lightweight AuthManager/Projects SOAP client

    Create by passing a WSDL URL:
        auth_projects = AuthProjectsClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(AuthProjectsClient, self).__init__(wsdl_url)

    def list_projects(self, token):
        return self.method_call('listProjects', [token])

    def create_project(self, token, project_name, description):
        return self.method_call('createProject', [token, project_name,
                                                  description])

    def delete_project(self, token, project_ID):
        return self.method_call('deleteProject', [token, project_ID])
