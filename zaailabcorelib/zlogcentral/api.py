import socket
import time
import requests
from grequests import Pool
import os
import json
request_pool = Pool(20)
def get_local_ip():
    local_ip = socket.gethostname()
    local_ip="10.40.34."+local_ip[-2:]
    return local_ip
def get_name_of_folder():
    env_name = os.getenv('NAME')
    if(env_name is None):
        path = os.getcwd()
        folder = os.path.basename(path)
    else:
        folder = env_name
    return folder

class LogJob():
    def __init__(self, uid, cmd):
        self.uid = uid
        self.cmd = cmd
        self.start_time = int(time.time()*1000)
        self.param = {}

    def __init__(self):
        self.uid = 0
        self.cmd = 0
        self.start_time = int(time.time() * 1000)
        self.param = {}

    def set_dict_param(self, param):
        self.param.update(param)
    def set_param(self, key, value):
        self.param[key]=value
    def get_start_time(self):
        return self.start_time
    def get_uid(self):
        return self.uid
    def get_cmd(self):
        return self.cmd
    def get_json_string(self):
        return json.dumps(self.param)

class LogClient:

    def __init__(self, host, port):
        self.host = host
        self.port = str(port)

    def __send_request(self, param):
        try:
            requests.post(param[0], data=param[1], timeout=1)
        except:
            pass

    def __general_log(self, category, log, path):
        project = get_name_of_folder()
        local_ip = get_local_ip()
        created_time = int(time.time()*1000)
        log_json={
            "project":project,
            "ip":local_ip,
            "created_time":created_time,
            "log":log

        }

        log = json.dumps(log_json)
        data = {
            'category': category,
            'log': log
        }
        param =[]
        param.append("http://" + self.host + ":" + self.port + path)
        param.append(data)
        request_pool.spawn(self.__send_request,param)
    def log(self, category, log):
        """
            log function

            :param category: category for the project (Ex : ZALO_FACE)
            :param log has 2 type:
                string: old flow. Just send user's json string
                LogJob: new flow. Send LogJob object with cmd, uid, execute_time are added to data
        """
        if (type(log) == LogJob):
            log_job = True
        else:
            log_job = False
        if(log_job):
            log.set_param("uid", log.get_uid())
            log.set_param("cmd", log.get_cmd())
            log.set_param("execute_time", int(time.time()*1000)-log.get_start_time())
            self.__general_log(category, log.get_json_string(), "/log")
        else:
            self.__general_log(category, log, "/log")