import os
import sys
from pprint import pprint

import clfpy

def main():
    if not len(sys.argv) == 6:
        print("Wrong number of arguments, requiring <name>, "
              + "<memory reservation>, <memory limit>, <container port>, "
              + "<environment-file path>")
        exit(1)

    srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

    # Read environment variables
    token = os.environ['CFG_TOKEN']

    name = sys.argv[1]
    memory_res = int(sys.argv[2])
    memory_lim = int(sys.argv[3])
    port = int(sys.argv[4])
    env_file = sys.argv[5]

    service_def = {
        "container-tag": "latest",
        "memory-reservation": memory_res,
        "memory-limit": memory_lim,
        "container-port": port,
        "environment": srv.read_env_file(env_file)
    }
    pprint(srv.update_service(token, name, service_def))

if __name__ == "__main__":
    main()

