import os
import sys
from pprint import pprint

sys.path.append(os.path.join(sys.path[0], '..'))
import clfpy

def main():
    if not len(sys.argv) == 3:
        print("Wrong number of arguments, requiring <name> and <docker source folder>")
        exit(1)

    srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

    # Read environment variables
    token = os.environ['CFG_TOKEN']

    name = sys.argv[1]
    docker_src = sys.argv[2]

    creds = srv.get_docker_credentials(token, name)
    srv.build_and_push_docker_image(token, name, docker_src, creds)

if __name__ == "__main__":
    main()

