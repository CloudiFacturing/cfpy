"""Simple SOAP client as base class for more specialized clients"""
from suds.client import Client
from suds.cache import NoCache
from suds import WebFault, MethodNotFound


class SoapClient(object):
    """Simple wrapper around a suds.client.Client object.

    Create by passing a wsdl url:
        client = SoapClient(<WSDL_URL>)

    Serves as a base class for more specialized clients.
    """
    def __init__(self, wsdl_url):
        self.wsdl_url = wsdl_url
        self.client = Client(self.wsdl_url, cache=NoCache())

    def method_call(self, methodname, method_args):
        """Calls an arbitrary SOAP method.

        Args:
            methodname (str): name of the method to call
            method_args (list): argument list to pass to the method

        Returns:
            SOAP response or SOAP fault object
        """
        try:
            method = getattr(self.client.service, methodname)
        except MethodNotFound as error:
            return error

        try:
            response = method(*method_args)
        except WebFault as error:
            return error

        return response
