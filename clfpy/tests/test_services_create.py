import os
from pprint import pprint

import clfpy

srv = clfpy.ServicesClient('https://api.hetcomp.org/servicectl-1/')

# Read environment variables
token = os.environ['CFG_TOKEN']
docker_source_folder = os.environ['DOCKER_SOURCE_FOLDER']
project = os.environ['CFG_PROJECT']

name = 'newservice'

pprint(srv.create_new_service(token, name))
creds = srv.get_docker_credentials(token, name)
srv.build_and_push_docker_image(token, name, docker_source_folder, creds)

service_def = {
    "container-tag": "latest",
    "memory-reservation": 100,
    "memory-limit": 150,
    "container-port": 80,
    "environment": [
        {"name": "CONTEXT_ROOT", "value": "/{}-{}".format(project, name)}
    ]
}
pprint(srv.update_service(token, name, service_def))
