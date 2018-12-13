import os
import sys
from pprint import pprint

import clfpy

def main():
    srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

    # Read environment variables
    token = os.environ['CFG_TOKEN']

    name = sys.argv[1]
    if len(sys.argv) == 3:
        tail = sys.argv[2]
    else:
        tail = 20

    srv.print_service_logs(token, name, tail=tail)

if __name__ == "__main__":
    main()
