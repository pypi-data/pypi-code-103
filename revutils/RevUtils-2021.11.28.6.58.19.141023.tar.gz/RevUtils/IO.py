import requests as req
import time
from . import Logger as Log


class ResponseBodyEmpty(Exception):
    def __init__(self):
        super().__init__('response body empty')


def print_exception(message, retry):
    Log.info(f'retry: {retry} ->')
    Log.info(message)


def get_url(url, retry_sleep=.5, retry=15, timeout=30, verify=False, stream=False):
    for i in range(retry):
        response = None
        try:
            response = req.get(url, timeout=timeout, verify=verify, stream=stream)
            if response is None:
                continue
            if response.status_code != 200:
                raise Exception(f'status code: {response.status_code}')
            if 'Content-Length' in response.headers \
                    and int(response.headers['Content-Length']) <= 0:
                raise ResponseBodyEmpty()
            return response
        except ResponseBodyEmpty as ex:
            print_exception(f'{ex}, {url}', i + 1)
            if i >= 1:
                break
        except Exception as ex:
            msg = f'ex: {ex.__str__()}'
            if response is not None:
                msg += f', {url}, {response.status_code}, {response.headers=}'
            print_exception(msg, i + 1)
        time.sleep(retry_sleep)
    return None


def get_url_raw(**kwargs):
    response = get_url(stream=True, **kwargs)
    return b'' if response is None else response.raw.data


def get_url_utf8(**kwargs):
    response = get_url(**kwargs)
    return '' if response is None else response.content.decode('utf8')


def write_bytes_to_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def download_to_file(url: str, path: str, raw=False, _return=False) -> bytes:
    response = get_url(url=url, stream=raw)

    if not response:
        raise Exception('invalid response from server received.')

    if raw:
        data = response.raw.data
    else:
        data = response.content

    write_bytes_to_file(path, data)

    if _return:
        return data
