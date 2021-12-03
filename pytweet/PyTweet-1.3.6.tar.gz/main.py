import os
import pytweet
from flask import Flask
app = Flask('app')

@app.route('/webhook/twitter')
def hello_world():
    return 'Hello, World!'

app.run(host='0.0.0.0', port=8080)









# def methods(obj):
#     for _ in dir(obj):
#         try:
#             e=getattr(obj, _, None)
#             print(_, e)
#         except Exception:
#             continue

client=pytweet.Client(
    os.environ["bearer_token"], 
    consumer_key=os.environ["api_key"], 
    consumer_key_secret=os.environ["api_key_secret"], 
    access_token=os.environ["my_token"],
    access_token_secret=os.environ["my_token_secret"]
)