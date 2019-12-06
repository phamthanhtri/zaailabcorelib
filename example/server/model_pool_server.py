import sys
sys.path.append('gen-py')
from thrift_file.Ping import Processor
from thrift_file.ttypes import TResult
from zaailabcorelib.zserver.thrift_server import TModelPoolServer
from zaailabcorelib.ztools.decorator import zlogging_deco
from zaailabcorelib.thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from zaailabcorelib.thrift.transport import TSocket
from zaailabcorelib.thrift.transport.TTransport import TFramedTransportFactory

class Handler():
    def __init__(self, model_path, gpu_id=-1, mem_fraction=0.0):
        self.model_path = model_path
        self.gpu_id = gpu_id
        self.mem_fraction = mem_fraction
        print(self.__dict__)

    @zlogging_deco(default_value=TResult(errorCode=-1, message="-1"))
    def pong(self, value):
        return TResult(errorCode=0, message=str(value) + "-" + self.model_path)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8100
    print("====================================")
    print("host: ", host)
    print("post: ", port)
    print("====================================")
    socket = TSocket.TServerSocket(host=host, port=port)
    pfactory = TBinaryProtocolFactory()
    tfactory = TFramedTransportFactory()
    list_model_config = [{'model_path': "/data/model.ckpt",
                          "gpu_id": 0,
                          "mem_fraction": 0.2},
                         {'model_path': "/data/model.ckpt",
                          "gpu_id": 0,
                          "mem_fraction": 0.2}]
    server = TModelPoolServer(handler_cls=Handler,
                              processor_cls=Processor,
                              list_model_config=list_model_config,
                              serverTransport=socket,
                              transportFactory=tfactory,
                              protocolFactory=pfactory,
                              )
    server.serve()
