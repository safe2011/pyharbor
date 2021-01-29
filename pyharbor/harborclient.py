#!/usr/bin/env python

import requests
import urllib3
import json
import logging
import traceback


requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

header_overrides = {"Content-Type": "application/json"}

logging.basicConfig(level=logging.INFO)




def _safe_loads(text):
    try:
        return json.loads(text)
    except Exception:
        return text


def make_client_result(response, raw=False):
    return _safe_loads(response.text)
    # ret = {"success": False, "httpcode": 0, "payload": {}, "error": {}}

    # ret["httpcode"] = response.status_code

    # if response.status_code in range(200, 299):
    #     ret["success"] = True
    #     if raw is True:
    #         ret["payload"] = response.text
    #     else:
    #         ret["payload"] = _safe_loads(response.text)

    # else:
    #     ret["success"] = False

    #     if raw is True:
    #         ret["error"] = response.text
    #     else:
    #         ret["error"] = _safe_loads(response.text)

    #     if not ret.get("error", None) and response.status_code in [401]:
    #         ret["error"] = "Unauthorized - please check your username/password"

    # return ret

class HarborClient(object):
    def __init__(self, host, user, password, protocol="http",ssl_verify=False):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.ssl_verify=ssl_verify
        self.page_size = 100
        ver = self._get_api_version()
        if len(ver)>0:
            self.base_url = "{}://{}/api/{}".format(self.protocol,self.host,ver)
        else:
            self.base_url = "{}://{}/api".format(self.protocol,self.host)


    def _get_api_version(self):
        url  = "{}://{}/api/version".format(self.protocol,self.host)
        try:
            _logger.debug("GET url=%s", str(url))
            _logger.debug("GET insecure=%s", str(self.ssl_verify))
            r = requests.get(url=url,
                verify=self.ssl_verify,
                headers=header_overrides,
                )            
            if r.status_code == 200:
                response = json.loads(r.text)
                return response.get("version","")
        except Exception as err:
            _logger.error(str(err))
            #raise err
        return ""
        



    # GET /projects
    def get_projects(self):
        ret  = []
        
        try:
            page = 1
            while True :
                url = '{}/projects?page={}&page_size={}'.format(self.base_url,page,self.page_size)
                _logger.debug("GET url=%s", str(url))
                r = requests.get(
                    url=url,
                    auth=(self.user,self.password),
                    verify=self.ssl_verify,
                    headers=header_overrides,
                    )   
                r = requests.get(
                        url=url,
                        auth=(self.user,self.password),
                        verify=self.ssl_verify,
                        headers=header_overrides,
                        )  

                if r.status_code in range(200, 299):    
                    response = json.loads(r.text)
                    for row in response:
                        ret.append(row.get("name"))
                    
                    if len(response) <  self.page_size:
                        break
                    
                    page += 1
                else:
                    raise Exception(r.text)
        except Exception as err:
            raise err
        return ret 

    def get_project_repository(self,project_name):
        ret  = []
        
        try:
            page = 1
            while True:
                url = "{}/projects/{}/repositories?page={}&page_size={}".format(
                    self.base_url,
                    project_name,
                    page,
                    self.page_size)
                _logger.debug("GET url=%s", str(url))

                r = requests.get(
                    url=url,
                    auth=(self.user,self.password),
                    verify=self.ssl_verify,
                    headers=header_overrides,
                    )  

                if r.status_code in range(200, 299):    
                    response = json.loads(r.text)
                    for row in response:
                        repo = row.get("name","")
                        if repo.startswith(project_name+"/"):
                            repo = repo[len(project_name)+1:]
                        ret.append(repo)
                    
                    if len(response) <  self.page_size:
                        break

                    page += 1
                else:
                    raise Exception(r.text)

        except Exception as err:
            raise err
        return ret 
    
    def get_project_repository_artifacts(self,project_name,repository_name):
        ret  = []
        
        try:
            page = 1
            while True: 
                url = "{}/projects/{}/repositories/{}/artifacts?page={}&page_size={}".format(self.base_url,project_name,repository_name,page,self.page_size)
                _logger.debug("GET url=%s", str(url))
                r = requests.get(
                    url=url,
                    auth=(self.user,self.password),
                    verify=self.ssl_verify,
                    headers=header_overrides,
                    )       
                r = requests.get(
                    url=url,
                    auth=(self.user,self.password),
                    verify=self.ssl_verify,
                    headers=header_overrides,
                    )  

                if r.status_code in range(200, 299):    
                    response = json.loads(r.text)
                    for row in response:
                        tags  = row.get("tags",[])
                        ret.append(tags[0].get("name"))
                    
                    if len(response) <  self.page_size:
                        break

                    page += 1
                else:
                    raise Exception(r.text)
        except Exception as err:
            raise err
        return ret 
    def get_project_tags(self,project_name):
        ret = []
        try:
            repo_list = self.get_project_repository(project_name)
            for repo in repo_list:
                # if repo.startswith(project_name+"/"):
                #     repo = repo[len(project_name)+1:]
                tags = self.get_project_repository_artifacts(project_name,repo)
                for tag in tags:
                    ret.append("{}/{}/{}:{}".format(self.host,project_name,repo,tag))

        except Exception as err:
            raise err
        return ret 
       