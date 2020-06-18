import sys
sys.path.append("..")
sys.path.append(".")
from zaailabcorelib.http_server import Server

from flask import request, jsonify

def test_func():
    data = request.form
    print(data)
    return jsonify({
        "test":"test"
    }),200, {"content-type":"application/json"}

def test_func1():
    return jsonify({
        "test1":"ok man"
    }),200, {"content-type":"application/json"}

list_dict = [{
    "path":"/test",
    "methods":["GET", "POST"],
    "function":test_func
},{
    "path":"/test1",
    "methods":["GET", "POST"],
    "function":test_func1
}]
server = Server(list_dict)
server.run()