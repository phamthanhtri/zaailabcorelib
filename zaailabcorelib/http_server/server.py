from waitress import serve
import zaailabcorelib.http_server.setting as setting
from flask import Flask


class Server:
    def __init__(self, list_dict,name="server"):
        print(list_dict)
        self.name = name
        self.app = Flask(name)
        for i in range(len(list_dict)):
            self.app.add_url_rule(list_dict[i]["path"], "function_"+list_dict[i]["path"], list_dict[i]["function"], methods=list_dict[i]["methods"])


    def run(self):
        host = setting.cons.ARGS[self.name + '@host']
        port = setting.cons.ARGS[self.name + '@port']
        print(host)
        print(port)
        if (str.lower(setting.cons.ARGS[self.name + '@debug']) == 'true'):
            print("debug: true")
            self.app.run(host=host, port=port, debug=setting.cons.ARGS[self.name + '@debug'])
        else:
            print("debug: false")
            serve(app=self.app, host=host, port=port, threads=100)