'''https://medium.com/google-cloud/optimizing-tensorflow-models-for-serving-959080e9ddbf
'''

import tensorflow as tf
from keras import backend as K
from tensorflow.tools.graph_transforms import TransformGraph
from tensorflow.python import ops
import os

def get_size(model_dir, model_file='saved_model.pb'):
    '''Get size of graph model'''
    model_file_path = os.path.join(model_dir, model_file)
    print(model_file_path, '')
    pb_size = os.path.getsize(model_file_path)
    variables_size = 0
    if os.path.exists(\
        os.path.join(model_dir,'variables/variables.data-00000-of-00001')):
    
        variables_size = os.path.getsize(os.path.join(\
                                                      model_dir,'variables/variables.data-00000-of-00001'))
        variables_size += os.path.getsize(os.path.join(\
                                                       model_dir,'variables/variables.index'))
    print('Model size: {} KB'.format(round(pb_size/(1024.0),3)))
    print('Variables size: {} KB'.format(round( variables_size/(1024.0),3)))
    print('Total Size: {} KB'.format(round((pb_size + variables_size)/(1024.0),3)))


def convert_graph_def_to_saved_model(export_dir, graph_filepath, output_key, output_node_name):
  if tf.gfile.Exists(export_dir):
    tf.gfile.DeleteRecursively(export_dir)
  graph_def = get_graph_def_from_file(graph_filepath)
  with tf.Session(graph=tf.Graph()) as session:
    tf.import_graph_def(graph_def, name='')
    tf.saved_model.simple_save(
        session,
        export_dir,
        inputs={
            node.name: session.graph.get_tensor_by_name(
                '{}:0'.format(node.name))
            for node in graph_def.node if node.op=='Placeholder'},
        outputs={output_key: session.graph.get_tensor_by_name(
            output_node_name)}
    )
    print('****************************************')
    print('Optimized graph converted to SavedModel!')
    print('****************************************')


# Optimizing the graph via TensorFlow library
def optimize_graph(model_dir, graph_filename, transforms, input_names, output_names, outname='optimized_model.pb'):
    graph_def = get_graph_def_from_file(os.path.join(model_dir, graph_filename))
    optimized_graph_def = TransformGraph(
                          graph_def,
                          input_names,  
                          output_names,
                          transforms)
    tf.train.write_graph(optimized_graph_def,
                      logdir=model_dir,
                      as_text=False,
                      name=outname)
    print('Graph optimized!')
    
def get_graph_def_from_file(graph_filepath):
    with ops.Graph().as_default():
        with tf.gfile.GFile(graph_filepath, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            return graph_def


TRANSFORMS = [
    'remove_nodes(op=Identity)',
    'fold_constants(ignore_errors=true)',
    'merge_duplicate_nodes',
    'strip_unused_nodes',
    'fold_batch_norms'
]





def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    from tensorflow.python.framework.graph_util import convert_variables_to_constants
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        # Graph -> GraphDef ProtoBuf
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = convert_variables_to_constants(session, input_graph_def,
                                                      output_names, freeze_var_names)
        return frozen_graph
    

def convert_h5df_to_pb(folder_to_save, model_name, session, model, keep_var_names=None, output_names=None):
    if not os.path.isdir(folder_to_save):
        os.makedirs(folder_to_save)
    
    frozen_graph = freeze_session(session,
                                  output_names=[out.op.name for out in model.outputs])
    tf.train.write_graph(frozen_graph, 
                         folder_to_save, 
                         model_name, 
                         as_text=False)
    print('Saved model to {} with name `{}`'.format(folder_to_save, model_name))
    

# Example
# import tensorflow as tf
# import keras
# import keras.backend as K

# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# # Config Device
# config = tf.ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.3
# sess = tf.Session(config=config)
# set_session(sess)

# # Load keras model
# model_dir = ""
# model = keras.load_model(filepath=model_dir, compile=False)
# convert_h5df_to_pb("freeze_model", "model.pb", K.get_session(), model)

def main():
    '''Example'''   
    # Optimize graph using TransformGraph 
    optimize_graph('client', 'motorbike_classification_inception_net_128_v4_e36.pb', 
                    TRANSFORMS, 
                    input_names=['input_0:0'],
                    output_names=['activation_95/Sigmoid:0', 'global_average_pooling2d_1/Mean:0'],
                    outname='optimized_model.pb')