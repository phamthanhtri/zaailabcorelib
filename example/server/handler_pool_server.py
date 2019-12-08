import sys
sys.path.append('gen-py')
sys.path.append('/Users/congvo/Workspace/zaailabcorelib/')
import numpy as np
from zaailabcorelib.thrift.transport.TTransport import TFramedTransportFactory
from zaailabcorelib.thrift.transport import TSocket
from zaailabcorelib.thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from zaailabcorelib.ztools.decorator import zlogging_deco
from zaailabcorelib.zserver.thrift_server import TMultiPoolServer, TModelBase, THandlerBase
from thrift_file.ttypes import TResult
from thrift_file.Ping import Processor


class CoreCompute():
    def __init__(self, model_config):
        print("Init Model")
        self.model_path = model_config.get('model_path')
        self.gpu_id = model_config.get('gpu_id')
        self.mem_fraction = model_config.get('mem_fraction')

        # import tensorflow as tf
        # self.graph = tf.Graph()
        # with self.graph.as_default():
        #     self.x = tf.placeholder(dtype=tf.int32)
        #     self.y = self.x + 10
        # self.sess = tf.Session(graph=self.graph)

    def predict(self, x):
        # with self.graph.as_default():
        #     print("predict: ", x)
        #     print(self.x)
        #     print(self.y)
        #     result = self.sess.run([self.y], feed_dict={self.x: x})        
        # print("predict - result: ", result)
        result = x
        return result


class Model(TModelBase):
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

class Handler(THandlerBase):
    def __init__(self, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)

    def process_input(self, input):
        return input

    # @zlogging_deco(default_value=TResult(errorCode=-1, message="-1"))
    def pong(self, value):
        # print(value)
        result = self.send_to_model(value)
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
    tfactory = TFramedTransportFactory()

    list_model_config = [{'model_path': "/data/model.ckpt",
                          "gpu_id": 0,
                          "mem_fraction": 0.2}]
    server = TMultiPoolServer(handler_cls=Handler,
                              processor_cls=Processor,
                              model_cls=Model,
                              list_model_config=list_model_config,
                              lsocket=lsocket,
                              inputProtocolFactory=pfactory,
                              outputProtocolFactory=pfactory,
                              batch_timeout=0.05,
                              n_handlers=1
                              )
    server.serve()
