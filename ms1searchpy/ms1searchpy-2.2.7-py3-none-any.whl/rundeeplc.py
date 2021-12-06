import subprocess

deeplc_path = '/home/mark/virtualenv_deeplc/bin/deeplc'
outres_name = '/home/mark/deeplc_res.txt'
outtest_name = '/home/mark/deeplc_test.txt'
outtrain_name = '/home/mark/deeplc_train.txt'

subprocess.call([deeplc_path, '--file_pred', outtest_name, '--file_cal', outtrain_name, '--file_pred_out', outres_name])
