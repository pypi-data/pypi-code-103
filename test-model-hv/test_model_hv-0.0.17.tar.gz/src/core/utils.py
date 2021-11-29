import tensorflow as tf
import os
import git
import tempfile
import shutil
import json


def get_folder_name(path, prefix=''):
    """
    Look at the current path and change the name of the experiment
    if it is repeated

    Args:
        path (string): folder path
        prefix (string): prefix to add

    Returns:
        string: unique path to save the experiment
"""

    if prefix == '':
        prefix = path.split('/')[-1]
        path = '/'.join(path.split('/')[:-1])

    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    if prefix not in folders:
        path = os.path.join(path, prefix)
    elif not os.path.isdir(os.path.join(path, '{}_0'.format(prefix))):
        path = os.path.join(path, '{}_0'.format(prefix))
    else:
        n = sorted([int(f.split('_')[-1]) for f in folders if '_' in f[-2:]])[-1]
        path = os.path.join(path, '{}_{}'.format(prefix, n+1))

    return path

def standardize(tensor, axis=0, return_mean=False):
    """
    Standardize a tensor subtracting the mean

    Args:
        tensor (1-dim tensorflow tensor): values
        axis (int): axis on which we calculate the mean
        return_mean (bool): output the mean of the tensor
                            turning on the original scale
    Returns:
        tensor (1-dim tensorflow tensor): standardize tensor
    """
    mean_value = tf.reduce_mean(tensor, axis, name='mean_value')
    z = tensor - tf.expand_dims(mean_value, axis)

    if return_mean:
        return z, mean_value
    else:
        return z




def load_weights(git_link , model_name, overwrite=True):
    
    model_name="astromer_10022021"
    git_link="https://github.com/HarshVardhanGoyal/test_model.git"
    model_path = os.path.join(os.getcwd(),"weights")

    try: 
        test_dir = tempfile.mkdtemp()
        git.Repo.clone_from(git_link, test_dir, branch='main', depth=1)
        time.sleep(2)
        if os.path.isdir(model_path):
            if overwrite:
                shutil.rmtree(model_path)
            else:
                print("The saved weights already exists")
    except:
        print("Couldn't load the model")
    finally:
        sourcepath = os.path.join(test_dir, model_name)
        sourcefiles = os.listdir(sourcepath)
        destinationpath = os.path.join(model_path, model_name)
        os.makedirs(destinationpath)
        for file in sourcefiles:
            if file.endswith('.index') or file.endswith('.data-00000-of-00001') or file.endswith('.json') or file.endswith("checkpoint"):
                print(sourcefiles)
                print(destinationpath)
                print(file)
                shutil.move(os.path.join(sourcepath,file), os.path.join(destinationpath,file))

    #shutil.move(os.path.join(test_dir, model_name), model_path)
    # shutil.rmtree(test_dir)



    # Loading the model
    if os.path.isdir(model_path):
        model = model.load_weights(os.path.join(destinationpath, "weights"))
    return model