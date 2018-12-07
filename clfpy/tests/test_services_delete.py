import os
from pprint import pprint

import clfpy

srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

# Read environment variables
token = os.environ['CFG_TOKEN']

name = 'newservice'

pprint(srv.delete_service(token, name))
