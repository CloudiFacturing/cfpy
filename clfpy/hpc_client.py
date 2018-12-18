"""Lightweight SOAP client to communicate with the HPC service"""
from clfpy import SoapClient


class ImageNotFoundException(Exception):
    pass


class ImageSourceNotFoundException(Exception):
    pass


class ImageNameIllegalException(Exception):
    pass


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
        res = self.method_call('getImageInfo', [token, image_name])
        if "404: Image not found" in str(res):
            raise ImageNotFoundException
        if "400: Image name or source file path illegal" in str(res):
            raise ImageNameIllegalException

        return res

    def register_image(self, token, target_name, source_gss_ID):
        res = self.method_call('registerImage', [token, target_name, source_gss_ID])
        if "404: Image source file not found" in str(res):
            raise ImageSourceNotFoundException
        if "400: Image name or source file path illegal" in str(res):
            raise ImageNameIllegalException
        return res

    def update_image(self, token, target_name, source_gss_ID):
        res = self.method_call('updateImage', [token, target_name, source_gss_ID])
        if "404: Image source file not found" in str(res):
            raise ImageSourceNotFoundException
        if "400: Image name or source file path illegal" in str(res):
            raise ImageNameIllegalException
        return res
    
    def delete_image(self, token, image_name):
        return self.method_call('deleteImage', [token, image_name])
