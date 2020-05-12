import grequests
import socket
import time


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

class LogClient:

    def __init__(self, host, port, path="/log"):
        self.host = host
        self.port = str(port)
        self.path = path

    def log(self, category, log):
        local_ip = get_local_ip()
        created_time = int(time.time())
        log = local_ip + '\t' + str(created_time) + '\t' + log
        data = {
            'category': category,
            'log': log
                }
        res = grequests.post("http://"+self.host+":"+self.port+self.path, data = data)
        return res