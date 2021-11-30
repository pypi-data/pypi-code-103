import json

BASE_URI = 'https://fantasysports.yahooapis.com/fantasy/v2/'


def yahoo_query(oauth2_token, url):
    url = BASE_URI + url + '?format=json'
    response = oauth2_token.session.get(url)
    json_data = json.loads(str(response.content, 'utf-8'))
    return json_data
