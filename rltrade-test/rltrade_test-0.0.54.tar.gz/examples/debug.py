import time 
import threading
from rltrade.ibkr import api_connect, get_stock_info

app = api_connect(demo=True)
def run_loop():
	    app.run()

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

app.reqMatchingSymbols(1,"ES")
time.sleep(1)

app.disconnect()