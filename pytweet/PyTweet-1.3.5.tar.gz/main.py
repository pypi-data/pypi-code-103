import os
import pytweet
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

app.run(host='0.0.0.0', port=8080)

# def methods(obj):
#     for _ in dir(obj):
#         e=getattr(obj, _, None)
#         print(_, e)

# client=pytweet.Client(
#     os.environ["bearer_token"], 
#     consumer_key=os.environ["api_key"], 
#     consumer_key_secret=os.environ["api_key_secret"], 
#     access_token=os.environ["my_token"],
#     access_token_secret=os.environ["my_token_secret"]
# )
# tweet=client.fetch_tweet(1466285747372060676)
# methods(tweet.media[0])