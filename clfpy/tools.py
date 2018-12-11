"""Collection of convenience functions for CloudFlow services"""

class ExtraParameters():

    def __init__(self, extraParametersString):
        """Parses an extra-parameters string into a dict.
        The extra parameters as delivered from the workflow manager are encoded
        in a single string of the format "key1=value1,key2=value2,...".
        Important: The string contains another comma at the very end.
        """
        self.pars = {pair.split('=')[0]: pair.split('=')[1] for pair in
                     extraParametersString.split(',')[:-1]}

    def get_GSS_WSDL_URL(self):
        return self.pars['gss']

    def get_auth_WSDL_URL(self):
        return self.pars['auth']

    def get_WFM_endpoint(self):
        return self.pars['WFM']

    def get_filechooser_URL(self):
        return self.pars['phpFileChooser']

    def get_newworkflow_URL(self):
        return self.pars['newWorkflowUrl']
