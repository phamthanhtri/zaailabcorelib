
import cv2
import numpy as np
from PIL import Image


def load_image(path_to_load, mode='cv', channel_format='rgb'):
    mode = mode.lower()
    channel_format = channel_format.lower()
    assert mode in ['cv', 'pil'], ValueError('`mode` must be in [\'cv\', \'pil\']')
    assert channel_format in ['rgb', 'bgr'], ValueError('`mode` must be in [\'rgb\', \'bgr\']')
    if mode == 'cv':
        img_arr = cv2.imread(path_to_load)
        if channel_format == 'rgb':
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
        return img_arr
    else:
        img_pil = Image.open(path_to_load)
        if channel_format == 'rgb':
            img_pil = img_pil.convert('RGB')
        elif channel_format == 'bgr':
            img_pil = img_pil.convert('BGR')
        return img_pil
    

def encode_image(image_arr, ext="jpg", format_params=None):
    img_as_string = cv2.imencode("." + ext, image_arr, params=format_params)[1].tostring()
    img_as_hex = img_as_string.hex()
    return img_as_hex

    
def decode_image(img_as_hex):
    img_as_bytes = bytes.fromhex(img_as_hex)
    img_arr = cv2.imdecode(np.frombuffer(img_as_bytes, dtype=np.uint8), 1)
    return img_arr