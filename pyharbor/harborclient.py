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

class HarborBase(object):
    def __init__(self, host, user, password, protocol="http",ssl_verify=False):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.ssl_verify=ssl_verify
        self.page_size = 100
        self.api_version = self._get_api_version()
        if len(self.api_version)>0:
            self.base_url = "{}://{}/api/{}".format(self.protocol,self.host,self.api_version)
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
 
class HarborBaseClient(HarborBase):
    
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

class HarborV1Client(HarborBaseClient):
    def get_project_by_name(self,name):
        ret = {}
        try:
            url = "{}/projects?name={}".format(self.base_url,name)
            _logger.debug("GET url=%s", str(url))
            _logger.debug("GET insecure=%s", str(self.ssl_verify))
            r = requests.get(url=url,
                verify=self.ssl_verify,
                headers=header_overrides,
                )            
            if r.status_code == 200:
                response = json.loads(r.text)
                if response is not None and  len(response)>0:
                    ret = response[0]
            else:
                raise Exception(r.text)
        except Exception as err:
            raise err
        return ret
    def get_project_repository(self,project_name):
        ret = []
        try:
            project = self.get_project_by_name(project_name)
            if project is not None:
                project_id = project.get("project_id",None)
                if project_id is not None:
                    page = 1
                    while True:
                        url = "{}/repositories?project_id={}&page={}&page_size={}".format(self.base_url,project_id,page,self.page_size)
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
    
    def get_project_tags(self,project_name):
        ret = []
        try:
            repo_list = self.get_project_repository(project_name)
            for repo in repo_list:
                page = 1
                while True:
                    url = "{}/repositories/{}/{}/tags?page={}&page_size={}".format(
                        self.base_url,
                        project_name,
                        repo,
                        page,
                        self.page_size
                        )
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
                            tag = row.get("name","")
                            ret.append("{}/{}/{}:{}".format(self.host,project_name,repo,tag))
                          
                        if len(response) <  self.page_size:
                            break

                        page += 1
                    else:
                        raise Exception(r.text)
        except Exception as err:
            raise err
        return ret

class HarborV2Client(HarborBaseClient):
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
                url = "{}/projects/{}/repositories/{}/artifacts?page={}&page_size={}".format(
                    self.base_url,
                    project_name,
                    repository_name,
                    page,
                    self.page_size
                    )
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
class HarborClient(HarborBase):
    def __init__(self, host, user, password, protocol="http",ssl_verify=False):
        super().__init__(host=host,user=user,password=password,protocol=protocol,ssl_verify=ssl_verify)
        if len(self.api_version)>0:
            self.hc = HarborV2Client(host=host,user=user,password=password,protocol=protocol,ssl_verify=ssl_verify)
        else:
            self.hc = HarborV1Client(host=host,user=user,password=password,protocol=protocol,ssl_verify=ssl_verify)


    # GET /projects
    def get_projects(self):
        return self.hc.get_projects()

    def get_project_repository(self,project_name):
        return self.hc.get_project_repository(project_name)
    
    def get_project_tags(self,project_name):
        return self.hc.get_project_tags(project_name)
     
       