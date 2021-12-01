from urllib.request import ssl, socket
from datetime import date, datetime
import pytz
    
def cert_validate_date(hostname, port = 443)->datetime:
    """
    Validate the certificate expiration date
    """
    with socket.create_connection((hostname, port)) as sock:
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print("SSL version: " + ssock.version())
            cert = ssock.getpeercert()
            expire_date = cert["notAfter"]
            print ("Expire time: " + expire_date)
            gmt = pytz.timezone('GMT')
            dt = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")
            tzdt = gmt.localize(dt)
            print (tzdt)
            print (tzdt.astimezone().strftime("%Y-%m-%d %H:%M:%S %z"))
            return tzdt.astimezone()
