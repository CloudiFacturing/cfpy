"""Lightweight SOAP client to communicate with the HPC service"""
from clfpy import SoapClient


class HpcImagesClient(SoapClient):
    """Lightweight HPCInterface/Images SOAP client

    Create by passing a WSDL URL:
        hpc_images = HpcImagesClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(HpcImagesClient, self).__init__(wsdl_url)

    def list_images(self, token):
        return self.method_call('listImages', [token])

    def get_image_info(self, token, image_name):
        return self.method_call('getImageInfo', [token, image_name])

    def register_image(self, token, target_name, source_gss_ID):
        return self.method_call('registerImage', [token, target_name, source_gss_ID])

    def update_image(self, token, target_name, source_gss_ID):
        return self.method_call('updateImage', [token, target_name, source_gss_ID])
    
    def delete_image(self, token, image_name):
        return self.method_call('deleteImage', [token, image_name])