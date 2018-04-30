"""Lightweight SOAP client to communicate with the workflow manager"""
from clfpy import SoapClient


class WfmClient(SoapClient):
    """Lightweight workflow-manager SOAP client

    Create by passing a WSDL URL:
        wfm = WfmClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(WfmClient, self).__init__(wsdl_url)

    def serviceExecutionFinished(self, serviceID, sessionToken, xmlOutputs_base64):
        """Notifies the WFM that an application service has finished.
        
        'xmlOutputs_base64' is a base64-encoded string of the following form:
        
        <ServiceOutputs>
            <service_output1>...</service_output1>
            <service_output2>...</service_output2>
            ...
        </ServiceOutputs>
        """
        return self.method_call('serviceExecutionFinished',
                                [serviceID, sessionToken, xmlOutputs_base64])