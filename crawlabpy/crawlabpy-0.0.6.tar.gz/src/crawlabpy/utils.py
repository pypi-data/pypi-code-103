import json
import os
import paramiko
import requests
from crawlabpy.datapool import get_target_config
from crawlabpy.encoder import JSONEncoder


def notify_target(item, files):
    json_encoder = JSONEncoder()
    target = get_target_config()
    response = requests.post(target.Notify, json={
        'files': files,
        'record': json_encoder.encode(item)
    })
    if response.status_code == 200:
        response = json.loads(response.text)
        if response['status'] != 'ok':
            print('notify target error:{}'.format(response['message']))


# 上传文件
def save_file(name, data):
    # 获取配置
    target = get_target_config()
    local = '/tmp/{}'.format(name)
    remote = os.path.join(target.Path, name)
    # 将图片写到本地
    with open(local, 'wb+') as img:
        img.write(data)
    sf = paramiko.Transport((target.Host, int(target.Port)))
    sf.connect(username=target.Username, password=target.Password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):
            for f in os.listdir(local):
                sftp.put(os.path.join(local + f), os.path.join(remote + f))
        else:
            sftp.put(local, remote)
    except Exception:
        print('upload error:')
    sf.close()
    os.unlink(local)
