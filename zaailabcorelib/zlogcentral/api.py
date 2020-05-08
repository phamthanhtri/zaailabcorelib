import requests
class LogClient:

    def __init__(self, host, port, path="/log"):
        self.host = host
        self.port = str(port)
        self.path = path
    def log(self, category, log):
        data = {
            'category': category,
            'log': log
                }
        res = requests.post("http://"+self.host+":"+self.port+self.path, data)
        return res