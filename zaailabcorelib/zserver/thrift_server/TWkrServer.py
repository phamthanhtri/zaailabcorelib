
import time
from queue import Empty
from multiprocessing import Queue
import multiprocessing
import logging
import select
import socket
from collections import deque
from six.moves import queue
from zaailabcorelib.thrift.transport import TTransport
from zaailabcorelib.thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from .utils import current_milli_time, current_nano_time

import traceback
from zaailabcorelib.thrift.transport.TTransport import TTransportException
from zaailabcorelib.thrift.protocol import TBinaryProtocol
import warnings

logger = logging.getLogger(__name__)

# __all__ = ['TMultiPoolServer', 'TModelBase', 'THandlerBase']
# __all__ = ['TModelServer', 'TModelPoolServer']


class TModelBase(multiprocessing.Process):
    def __init__(self, inference_queue, result_dict, model_config, batch_infer_size=1, batch_group_timeout=10):
        super(TModelBase, self).__init__()
        self.inference_queue = inference_queue
        self.result_dict = result_dict
        self.batch_infer_size = batch_infer_size
        self.batch_group_timeout_in_sec = self._microsec_to_sec(
            batch_group_timeout)
        self.batch_group_timeout = batch_group_timeout
        self.model = self.model_init(model_config)

    def _microsec_to_sec(self, microsec):
        return microsec/1000

    def model_init(self, model_config: dict):
        raise NotImplementedError

    def predict(self, list_input):
        raise NotImplementedError

    def run(self):
        list_inference = []
        list_request_id = []
        while True:
            t = current_milli_time()
            while (len(list_inference) < self.batch_infer_size) and current_milli_time() - t < self.batch_group_timeout_in_sec:
                try:
                    [request_id, inp] = self.inference_queue.get(block=False)
                    list_inference.append(inp)
                    list_request_id.append(request_id)
                except Empty:
                    pass
                t = current_milli_time()

            if len(list_inference) > 0:
                list_result = self.predict(list_inference)
                for [_id, res] in zip(list_request_id, list_result):
                    self.result_dict.update({_id:res})
                list_request_id.clear()
                list_inference.clear()

    # def run(self):
    #     list_inference = []
    #     list_request_id = []
    #     while True:
    #         while True:
    #             try:
    #                 # , timeout=self.batch_timeout_in_sec)
    #                 [request_id, inp] = self.inference_queue.get(block=False)
    #                 list_inference.append(inp)
    #                 list_request_id.append(request_id)
    #                 if (len(list_inference) < self.batch_infer_size):
    #                     continue
    #             except Empty:
    #                 break
    #         if len(list_inference) != 0:
    #             list_result = self.predict(list_inference)
    #             for [_id, res] in zip(list_request_id, list_result):
    #                 self.result_dict.update({_id: res})
    #             list_request_id.clear()
    #             list_inference.clear()


class THandlerBase():
    def __init__(self, inference_queue, result_dict):
        self.inference_queue = inference_queue
        self.result_dict = result_dict

    def send_to_model(self, input_val):
        request_id = current_nano_time()
        input_ = self.process_input(input_val)
        self.inference_queue.put([request_id, input_], block=False)
        done = False
        while not done:
            result = self.result_dict.get(request_id, None)
            if result is not None:
                done = True
        return result

    def process_input(self, input):
        raise NotImplementedError


class ConnectionSink(multiprocessing.Process):
    """Worker is a small helper to process incoming connection."""

    def __init__(self, *args, **kwargs):
        super(ConnectionSink, self).__init__()
        self.wrk_id = kwargs.get('wrk_id')
        
        self.connection_queue = kwargs.get('connection_queue')
        self.processor_cls = kwargs.get('processor_cls')
        self.handler_cls = kwargs.get('handler_cls')
        self.inference_queue = kwargs.get('inference_queue')
        self.result_dict = kwargs.get('result_dict')

        self.input_transport_factory = kwargs.get('input_transport_factory')
        self.output_transport_factory = kwargs.get('output_transport_factory')
        self.input_protocol_factory = kwargs.get('input_protocol_factory')
        self.output_protocol_factory = kwargs.get('output_protocol_factory')

        self.logger = kwargs.get('logger')
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        print(f"Init Connection Sink {self.wrk_id}")

    def run(self):
        """Process queries from task queue, stop if processor is None."""
        self.handler = self.handler_cls(
            inference_queue=self.inference_queue,
            result_dict=self.result_dict)
        self.processor = self.processor_cls(self.handler)
        while True:
            try:
                client = self.connection_queue.get()
                self.serve_client(self.processor, client)
            except (KeyboardInterrupt, SystemExit):
                return 0
            except Exception as x:
                tb = traceback.format_exc()
                self.logger.exception(tb)

    def serve_client(self, processor, client):
        """Process input/output from a client for as long as possible"""
        itrans = self.input_transport_factory.getTransport(client)
        otrans = self.output_transport_factory.getTransport(client)
        iprot = self.input_protocol_factory.getProtocol(itrans)
        oprot = self.output_protocol_factory.getProtocol(otrans)
        try:
            while True:
                processor.process(iprot, oprot)
        except TTransportException:
            pass
        except Exception as x:
            tb = traceback.format_exc()
            self.logger.exception(tb)
        itrans.close()
        if otrans:
            otrans.close()


class TModelServer():
    """Base interface for a server, which must have a serve() method.
    Three constructors for all servers:
    1) (serverTransport)
    2) (serverTransport, transportFactory, protocolFactory)
    """

    def __init__(self, serverTransport, transportFactory=None, protocolFactory=None):
        self.transportFactory = transportFactory
        if transportFactory is None:
            self.transportFactory = TTransport.TTransportFactoryBase()

        self.protocolFactory = protocolFactory
        if protocolFactory is None:
            self.protocolFactory = TBinaryProtocol.TBinaryProtocolFactory()

        self.__initArgs__(serverTransport,
                          self.transportFactory, self.transportFactory,
                          self.protocolFactory, self.protocolFactory
                          )

    def __initArgs__(self, serverTransport,
                     inputTransportFactory, outputTransportFactory,
                     inputProtocolFactory, outputProtocolFactory):
        self.serverTransport = serverTransport
        self.inputTransportFactory = inputTransportFactory
        self.outputTransportFactory = outputTransportFactory
        self.inputProtocolFactory = inputProtocolFactory
        self.outputProtocolFactory = outputProtocolFactory

    def serve(self):
        pass


class TWrkServer(TModelServer):
    ''' A server runs a pool of multiple models to serve single request
        Written by CongVM
    '''

    def __init__(self,
                 handler_cls,
                 processor_cls,
                 model_cls,
                 lsocket,
                 list_model_config,
                 transport_factory,
                 protocol_factory,
                 batch_infer_size=1,
                 batch_group_timeout=10,
                 n_models=2,
                 n_handlers=2,
                 logger=None):

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.model_cls = model_cls
        self.handler_cls = handler_cls
        self.processor_cls = processor_cls
        self.socket = lsocket

        self.server_transport = lsocket
        self.transport_factory = transport_factory
        self.protocol_factory = protocol_factory

        self.n_handlers = int(n_handlers)
        self.n_models = int(n_models)
        self.clients = {}
        self.connection_queue = multiprocessing.Queue()
        self.inference_queue = multiprocessing.Queue()
        self.result_dict = multiprocessing.Manager().dict()
        self.list_model_config = list_model_config
        if len(self.list_model_config) == 0:
            warnings.warn(
                "`list_model_config` should not be empty", RuntimeWarning)

        self.batch_infer_size = batch_infer_size
        self.batch_group_timeout = batch_group_timeout
        self.list_handlers = []
        self.list_models = []

        super(TWrkServer, self).__init__(
            serverTransport=self.server_transport,
            transportFactory=self.transport_factory,
            protocolFactory=self.protocol_factory)

    def set_model_config(self, list_model_config):
        """Set the number of worker threads that should be created"""
        self.list_model_config = list_model_config

    def set_post_fork_callback(self, callback):
        if not callable(callback):
            raise TypeError("This is not a callback!")
        self.post_fork_callback = callback

    # def worker_process(self, connection_queue, model_config):
    #     """Loop getting clients from the shared queue and process them"""
    #     handler = self.handler_cls(**model_config)
    #     processor = self.processor_cls(handler)
    #     if self.post_fork_callback:
    #         self.post_fork_callback()
    #     while True:
    #         try:
    #             client = connection_queue.get()
    #             self.serve_client(processor, client)
    #         except (KeyboardInterrupt, SystemExit):
    #             return 0
    #         except Exception as err:
    #             tb = traceback.format_exc()
    #             self.logger.exception(tb)

    # def serve_client(self, processor, client):
    #     """Process input/output from a client for as long as possible"""
    #     itrans = self.inputTransportFactory.getTransport(client)
    #     otrans = self.outputTransportFactory.getTransport(client)
    #     iprot = self.inputProtocolFactory.getProtocol(itrans)
    #     oprot = self.outputProtocolFactory.getProtocol(otrans)
    #     try:
    #         while True:
    #             processor.process(iprot, oprot)
    #     except TTransportException:
    #         pass
    #     except Exception as err:
    #         tb = traceback.format_exc()
    #         self.logger.exception(tb)
    #     itrans.close()
    #     if otrans:
    #         otrans.close()

    def prepare(self):
        """Start a fixed number of workers and put into queue"""

        for model_config in self.list_model_config:
            wrk_model = self.model_cls(inference_queue=self.inference_queue,
                                       result_dict=self.result_dict,
                                       model_config=model_config,
                                       batch_infer_size=self.batch_infer_size,
                                       batch_group_timeout=self.batch_group_timeout)
            wrk_model.start()
            self.list_models.append(wrk_model)

        for idx in range(self.n_handlers):
            wrk_conn = ConnectionSink(wrk_id=idx,
                                      processor_cls=self.processor_cls,
                                      handler_cls=self.handler_cls,
                                      inference_queue=self.inference_queue,
                                      result_dict=self.result_dict,
                                      connection_queue=self.connection_queue,
                                      input_transport_factory=self.transport_factory,
                                      output_transport_factory=self.transport_factory,
                                      input_protocol_factory=self.protocol_factory,
                                      output_protocol_factory=self.protocol_factory)
            wrk_conn.start()
            self.list_handlers.append(wrk_conn)

    def serve(self):
        self.prepare()

        # first bind and listen to the port
        self.serverTransport.listen()
        while True:
            try:
                client = self.serverTransport.accept()
                if not client:
                    continue
                self.connection_queue.put(client)
            except (SystemExit, KeyboardInterrupt):
                break
            except Exception as err:
                tb = traceback.format_exc()
                self.logger.exception(tb)
