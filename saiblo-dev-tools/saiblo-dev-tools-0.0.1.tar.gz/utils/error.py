import sys
from sys import stderr

from requests import Response


def request_failed(response: Response) -> None:
    stderr.write(f'请求出错了（{response.status_code}）：\n')
    stderr.write(f'{response.text}\n')
    stderr.write('请检查你的配置，或者联系 Saiblo 维护人员\n')
    sys.exit(-1)


def exception_handler(exception: Exception) -> None:
    stderr.write('脚本出错了：\n')
    stderr.write(f'{exception}\n')
    stderr.write('请检查你的配置，或者联系 Saiblo 维护人员\n')
    sys.exit(-1)
