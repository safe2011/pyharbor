#!/usr/bin/env python

import sys
sys.path.append("../")

from pyharbor import HarborClient

host = "demo.goharbor.io"
user = "safe2011"
password = "Abcd12345678!"


client = HarborClient(host, user, password,"https",True)
# v = client.get_api_version()#
# print(v)
# Get all projects
print(client.get_projects())

print(client.get_project_repository("system"))


#print(client.get_project_repository_artifacts("system","secret"))


print(client.get_project_tags("system"))
print(client.get_project_tags("library"))