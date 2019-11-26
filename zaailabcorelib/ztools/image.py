
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import os


def load_image_from_disk(path_to_load, mode='cv', channel_format='rgb'):
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
    

def load_image_from_url(url, mode='cv', channel_format='rgb'):
    response = requests.get(url)
    img_pil = Image.open(BytesIO(response.content))
    img_pil = img_pil.convert('RGB')
    if mode == 'cv':
        img_arr = np.array(img_pil, np.uint8)
        if channel_format == 'bgr':
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
        return img_arr

    elif mode == 'pil':
        if channel_format == 'bgr':
            img_pil = img_pil.convert('BGR')
        return img_pil
    
    
def load_image(path_or_url, mode='cv', channel_format='rgb', proxy=None):
    if proxy is not None:
        os.environ['https_proxy'] = proxy
        os.environ['http_proxy'] = proxy
    path_or_url = path_or_url.lower()
    mode = mode.lower()
    channel_format = channel_format.lower()
    assert mode in ['cv', 'pil'], ValueError('`mode` must be in [\'cv\', \'pil\']')
    assert channel_format in ['rgb', 'bgr'], ValueError('`mode` must be in [\'rgb\', \'bgr\']')
    if 'http://' in path_or_url or 'https://' in path_or_url:
        return load_image_from_url(path_or_url, mode, channel_format)
    else:
        return load_image_from_disk(path_or_url, mode, channel_format)
    

def encode_image(image_arr, ext="jpg", format_params=None):
    img_as_string = cv2.imencode("." + ext, image_arr, params=format_params)[1].tostring()
    img_as_hex = img_as_string.hex()
    return img_as_hex

    
def decode_image(img_as_hex):
    img_as_bytes = bytes.fromhex(img_as_hex)
    img_arr = cv2.imdecode(np.frombuffer(img_as_bytes, dtype=np.uint8), 1)
    return img_arr



# import sys
# import  matplotlib.pyplot as plt
# sys.path.append('/media/congvm/DATA/Workspace/zaailabcorelib/zaailabcorelib/ztools/')
# sys.path.append('/media/congvm/DATA/Workspace/zaailabcorelib/example/')

# from image import load_image
# url = "http://www.emmc-imae.org/wp-content/uploads/2012/11/slider2.jpg"
# img = load_image(url)
# print(img)
# plt.imshow(img)


# img = load_image('/media/congvm/DATA/Workspace/zaailabcorelib/example/slider2.jpg')