import requests


def get_public_ip():
    """
    Get my Public IP in Python
    ; https://pytutorial.com/python-get-public-ip
    :return:
    """
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify=True)

    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
        exit()

    data = response.json()

    return data['ip']


if __name__ == '__main__':
    print(get_public_ip())
