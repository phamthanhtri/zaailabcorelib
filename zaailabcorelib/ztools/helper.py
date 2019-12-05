import os

def get_tf_env(gpu_id=-1, mem_fraction=0):
    ''' Get Tensorflow environment
        Return:
            tf, config
    '''
    if isinstance(gpu_id, str):
        gpu_id = int(gpu_id)
        
    if gpu_id != -1:
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        
    import tensorflow as tf
    # if tf.__version__.split('.')[0] == '2':
    #     tf = tf.compat.v1

    config = tf.ConfigProto()
    if mem_fraction == 0:
        config.gpu_options.allow_growth = True
    else:
        config.gpu_options.per_process_gpu_memory_fraction = float(mem_fraction)
    return tf, config

