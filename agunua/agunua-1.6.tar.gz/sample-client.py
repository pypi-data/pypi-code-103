#!/usr/bin/python3

import Agunua
import Agunua.status
import sys

if len(sys.argv) <= 1:
    raise Exception("Usage: %s url ..." % sys.argv[0])

for url in sys.argv[1:]:
    u = Agunua.GeminiUri(url, get_content=True, parse_content=True, insecure=True)
    print(u)
    if u.network_success:
        if u.status_code == "20":
            print("%i bytes" % len(u.payload))
            if u.links is not None and u.links != []:
                print("Links: %s" % u.links)
        else:
            print("Status code is %s" % Agunua.status.codes[u.status_code])
    print("")
    
