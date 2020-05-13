import grequests
import socket
import time
import requests
def get_local_ip():
    local_ip = socket.gethostname()
    local_ip="10.40.34."+local_ip[-2:]
    return local_ip

class LogClient:

    def __init__(self, host, port):
        self.host = host
        self.port = str(port)

    def __send_request(self, param):
        requests.post(param[0], data=param[1])

    def __general_log(self, category, log, path):
        local_ip = get_local_ip()
        created_time = int(time.time())
        log = local_ip + '\t' + str(created_time) + '\t' + log
        data = {
            'category': category,
            'log': log
        }
        param =[]
        param.append("http://" + self.host + ":" + self.port + path)
        param.append(data)
        pool = grequests.Pool(1)
        pool.spawn(self.__send_request,param)
    def log(self, category, log):
        self.__general_log(category, log, "/log")