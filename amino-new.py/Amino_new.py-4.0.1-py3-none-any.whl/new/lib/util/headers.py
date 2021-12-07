from amino.lib.util import device
from amino import client
sid = None

gen_msg_sig = None

web = None

class Headers:
    def __init__(self, data = None, type = None, deviceId: str = None, sig: str = None,sid:str=None):
        if deviceId:
            dev = device.DeviceGenerator(deviceId=deviceId)
        else:
            dev = device.DeviceGenerator()

        headers = {
            "NDCLANG": "en",
            "NDC-MSG-SIG": gen_msg_sig,
            "NDCDEVICEID": dev.device_id,
            "SMDEVICEID": "b89d9a00-f78e-46a3-bd54-6507d68b343c",
            "NDCAUTH": f"sid={sid}",
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "service.narvii.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        lost_headers = {
            "NDCLANG": "en",
            "NDCDEVICEID": dev.device_id,
            "SMDEVICEID": "b89d9a00-f78e-46a3-bd54-6507d68b343c",
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "aminoapps.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        web_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "x-requested-with": "xmlhttprequest"
        }
        self.reg_headers= {
    'accept': '/',
    'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
    'content-length': '35',
    'content-type': 'application/json',
    'cookie':'auc=e72277dd1793efef0c5ba0db4d8; qca=P0-2125635587-1620259566756; G_ENABLED_IDPS=google; gads=ID=fd25c8819b58298c:T=1620259596:S=ALNI_MYgGClDj--AgWtT6Oa_pvn5ENBUcw; gdpr_cookie_agreee=1; exp=60-0; asc=; _ga_9SJ4LCCH1X=GS1.1.1631388103.11.0.1631388103.0; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1733508529.1620259566; _gid=GA1.2.18082541.1631388105; session=.eJwNyrEOgjAQANBfMTc7KMJCwoApEkl6LEXCLUTbRlooMQSFQPh3Wd70Vqg_enDPXvcjhOPw1UdQ-YkDNQ.YT0DBA.IsbCVSlbjfKGVp8ONzK0IpEZzZ8',
    'origin': 'https://aminoapps.com/',
    'referer': 'https://aminoapps.com/c/arabkpoper/home/',
    'sec-ch-ua-mobile':'?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'x-requested-with': 'xmlhttprequest'
}

        if data:
            lost_headers["Content-Length"] = str(len(data))
        if sid:
            lost_headers["NDCAUTH"] = f"sid={sid}"
            headers["NDCAUTH"] = f"sid={sid}"
            web_headers["cookie"]= f"sid={sid}"
        if type: lost_headers["Content-Type"] = type
        if sig: headers["NDC-MSG-SIG"] = sig
        if web: web_headers = web
        self.headers = headers
        self.lost_headers = lost_headers
        self.web_headers = web_headers
        
