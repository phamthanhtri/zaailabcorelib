import tensorflow as tf
from .helper import get_tf_env


class TFModelBase(object):
    def __init__(self, input_names, output_names, model_path, gpu_id=-1, mem_fraction=0):
        self.model_path = model_path
        self.tf, self.config = get_tf_env(gpu_id=gpu_id, mem_fraction=mem_fraction)
        self.graph = self.tf.Graph()
        self.sess = tf.Session(graph=self.graph, config=self.config)
        self.__load_graph()
        self.input_nodes, self.output_nodes = self.__get_io_nodes(input_names, output_names)


    def __load_graph(self):
        with self.graph.as_default():
            od_graph_def = self.tf.GraphDef()
            with self.tf.gfile.GFile(self.model_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')            

    def __get_io_nodes(self, input_names, output_names):
        input_nodes = []
        output_nodes = []
        for inp_name in input_names:
            input_nodes.append(self.graph.get_tensor_by_name('{}:0'.format(inp_name)))
        for out_name in output_nodes:
            output_nodes.append(self.graph.get_tensor_by_name('{}:0'.format(out_name)))
        return input_nodes, output_names

    def predict(self, inputs):
        feed_dict = dict(zip(self.input_nodes, inputs))
        with self.graph.as_default():
            outputs = self.sess.run(
                self.output_nodes,
                feed_dict=feed_dict)
        return outputs


# Example
# class TFModel(TFModelBase):
#     def __init__(self, **kwargs):
#        super(TFModel, self).__init__(**kwargs)
        
#     def create_io_tensors(self):
#         self.input = self.graph.get_tensor_by_name('input_1:0')
#         self.output = self.graph.get_tensor_by_name('output_x/Softmax:0')
        
#     def predict(self, img_expanded):
        
#         with self.graph.as_default():
#             output = self.sess.run(
#                 self.output,
#                 feed_dict={self.input: img_expanded})
#         return output