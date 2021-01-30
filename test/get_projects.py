#!/usr/bin/env python

import sys
sys.path.append("../")

from pyharbor import HarborClient

host = "demo.goharbor.io"
user = "safe9981"
password = "Abcd12345"


# host = "81.68.225.116:8080"
# user = "admin"
# password = "Harbor12345"



client = HarborClient(host, user, password,"http",False)
# v = client.get_api_version()#
# print(v)
# Get all projects
print(client.get_projects())

#print(client.get_project_repository("system"))


#print(client.get_project_repository_artifacts("system","secret"))



print(client.get_project_tags("library"))
print(client.get_project_tags("system"))