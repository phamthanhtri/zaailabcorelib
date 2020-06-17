import sys
sys.path.append('gen-py')

from thrift_file.Ping import Processor
from thrift_file.ttypes import TResult
from zaailabcorelib.zserver.thrift_server import TModelBase, THandlerBase
# from zaailabcorelib.zserver.thrift_server import TWrkServer
from zaailabcorelib.zserver.thrift_server.TWkrServer import TWrkServer
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

    def predict(self, input_val):
        with self.graph.as_default():
            print("predict: ", input_val)
            # result = self.sess.run(self.y, feed_dict={self.x: input_val})
            result = [input_val]
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
        batch = np.vstack(batch)
        print(batch)
        result = self.model.predict(batch)
        return result


class Handler(THandlerBase):
    def __init__(self, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)

    def process_input(self, input):
        return input

    # @zlogging_deco(default_value=TResult(errorCode=-1, message="-1"))
    def pong(self, value):
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
                          "mem_fraction": 0.2}]*4

    server = TWrkServer(handler_cls=Handler,
                        processor_cls=Processor,
                        model_cls=Model,
                        list_model_config=list_model_config,
                        lsocket=lsocket,
                        transport_factory=tfactory,
                        protocol_factory=pfactory, 
                        batch_group_timeout=1,
                        n_handlers=4
                        )
    server.serve()
