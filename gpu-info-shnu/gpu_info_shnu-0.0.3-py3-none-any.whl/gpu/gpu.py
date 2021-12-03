import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # or any {'0', '1', '2'}
'''
TF_CPP_MIN_LOG_LEVEL 取值 0 ： 0也是默认值，输出所有信息
TF_CPP_MIN_LOG_LEVEL 取值 1 ： 屏蔽通知信息
TF_CPP_MIN_LOG_LEVEL 取值 2 ： 屏蔽通知信息和警告信息
TF_CPP_MIN_LOG_LEVEL 取值 3 ： 屏蔽通知信息、警告信息和报错信息
'''
import tensorflow as tf
def gpu():
    tf_version=tf.__version__
    gpu=tf.config.list_physical_devices('GPU')
    return f'TensorFlow:{tf_version}\nGPU nummber:{len(gpu)}\nGPU Info:{gpu}'
print(gpu())
