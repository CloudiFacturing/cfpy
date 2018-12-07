import os
from pprint import pprint

import clfpy

srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

# Read environment variables
token = os.environ['CFG_TOKEN']

name = 'newservice'

srv.print_service_list(token)
srv.print_service_status(token, name)
srv.print_service_logs(token, name)
