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
    path = os.getcwd()
    folder = os.path.basename(path)
    return folder
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
        self.__general_log(category, log, "/log")