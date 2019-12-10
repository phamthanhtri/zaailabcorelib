import sys
sys.path.append('gen-py')
sys.path.append('/Users/congvo/Workspace/zaailabcorelib/')

from thrift_file.Ping import Processor
from thrift_file.ttypes import TResult
# from zaailabcorelib.thrift.server import TNonblockingServer
from zaailabcorelib.zserver.thrift_server import TNonblockingServer
from zaailabcorelib.ztools.decorator import zlogging_deco
from zaailabcorelib.thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from zaailabcorelib.thrift.transport import TSocket
from zaailabcorelib.thrift.transport.TTransport import TFramedTransportFactory
import numpy as np


class CoreCompute():
    def __init__(self, model_config):
        print("Init Model")
        self.model_path = model_config.get('model_path')
        self.gpu_id = model_config.get('gpu_id')
        self.mem_fraction = model_config.get('mem_fraction')

        import tensorflow as tf
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.x = tf.placeholder(dtype=tf.int32)
            self.y = self.x + 10
        self.sess = tf.Session(graph=self.graph)

    def predict(self, x):
        with self.graph.as_default():
            # print("predict: ", x)
            # print(self.x)
            # print(self.y)
            result = self.sess.run([self.y], feed_dict={self.x: x})
        # print("predict - result: ", result)
        return result


class Model():
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

    def model_init(self, model_config: dict):
        model = CoreCompute(model_config)
        return model

    def predict(self, list_input) -> list:
        batch = []
        for inp in list_input:
            batch.append(inp)
        # batch = np.vstack(batch)
        # print(batch)
        result = self.model.predict(batch)
        return result


class Handler():
    def __init__(self, *args, **kwargs):
        self.model_config = kwargs.get('model_config')
        self.model = CoreCompute(self.model_config)

    @zlogging_deco(default_value=TResult(errorCode=-1, message="-1"))
    def pong(self, value):
        result = self.model.predict(value)
        return TResult(errorCode=0, message=str(result))


if __name__ == "__main__":
    host = "localhost"
    port = 8100
    print("====================================")
    print("host: ", host)
    print("post: ", port)
    print("====================================")
    lsocket = TSocket.TServerSocket(host=host, port=port)
    pfactory = TBinaryProtocolFactory()

    model_config = {'model_path': "/data/model.ckpt",
                          "gpu_id": 0,
                          "mem_fraction": 0.2}
    handler = Handler(model_config=model_config)                          
    processor = Processor(handler)

    server = TNonblockingServer.TNonblockingServer(processor=processor,
                                lsocket=lsocket,
                                inputProtocolFactory=pfactory,
                                outputProtocolFactory=pfactory,
                                threads=10
                                )
    server.serve()
