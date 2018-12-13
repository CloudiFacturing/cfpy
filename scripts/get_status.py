import os
import sys
from pprint import pprint

import clfpy

def main():
    srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

    # Read environment variables
    token = os.environ['CFG_TOKEN']

    name = sys.argv[1]

    srv.print_service_status(token, name)

if __name__ == "__main__":
    main()
