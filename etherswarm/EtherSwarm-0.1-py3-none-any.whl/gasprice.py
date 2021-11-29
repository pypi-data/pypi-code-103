import requests

def gasPrice(t="standard"):
    # t should in slow, fast, standard
    return requests.get("https://gasnow.sparkpool.com/api/v3/gas/price").json()['data'][t]
