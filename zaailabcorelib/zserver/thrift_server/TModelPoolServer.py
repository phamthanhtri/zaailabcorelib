import logging
from multiprocessing import Process, Queue
import traceback
from zaailabcorelib.thrift.transport.TTransport import TTransportException
from zaailabcorelib.thrift.protocol import TBinaryProtocol
from zaailabcorelib.thrift.transport import TTransport
import warnings

__all__ = ['TModelServer', 'TModelPoolServer']


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


class TModelPoolServerV1(TModelServer):
    ''' A server runs a pool of multiple models to serve single request
        Written by CongVM
    '''

    def __init__(self, *args, **kwargs):
        self.logger = kwargs.get("logger", None)
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.logger.info("Using TModelPoolServerV1")
        self.handler_cls = kwargs.get("handler_cls")
        self.processor_cls = kwargs.get("processor_cls")

        self.list_model_config = kwargs.get("list_model_config", [])
        if len(self.list_model_config) == 0:
            warnings.warn(
                "`list_model_config` should not be empty", RuntimeWarning)

        self.serverTransport = kwargs.get("serverTransport")
        self.transportFactory = kwargs.get("transportFactory")
        self.protocolFactory = kwargs.get("protocolFactory")
        self.workers = []
        self.post_fork_callback = None
        self.connection_queue = Queue()

        super(TModelPoolServerV1, self).__init__(
            serverTransport=self.serverTransport,
            transportFactory=self.transportFactory,
            protocolFactory=self.protocolFactory)

    def set_model_config(self, list_model_config):
        """Set the number of worker threads that should be created"""
        self.list_model_config = list_model_config

    def set_post_fork_callback(self, callback):
        if not callable(callback):
            raise TypeError("This is not a callback!")
        self.post_fork_callback = callback

    def worker_process(self, connection_queue, model_config):
        """Loop getting clients from the shared queue and process them"""
        handler = self.handler_cls(**model_config)
        processor = self.processor_cls(handler)
        if self.post_fork_callback:
            self.post_fork_callback()
        while True:
            try:
                client = connection_queue.get()
                self.serve_client(processor, client)
            except (KeyboardInterrupt, SystemExit):
                return 0
            except Exception as x:
                tb = traceback.format_exc()
                self.logger.exception(tb)

    def serve_client(self, processor, client):
        """Process input/output from a client for as long as possible"""
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)
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

    def serve(self):
        """Start a fixed number of workers and put into queue"""
        for model_config in self.list_model_config:
            try:
                w = Process(target=self.worker_process, args=(
                    self.connection_queue, model_config, ))
                w.daemon = True
                w.start()
                self.workers.append(w)
            except Exception as x:
                tb = traceback.format_exc()
                self.logger.exception(tb)

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
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.exception(tb)


class TModelPoolServer(TModelPoolServerV1):
    def __init__(self, *args, **kwargs):
        super(TModelPoolServer, self).__init__(*args, **kwargs)
