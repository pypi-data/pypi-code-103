import requests
import json
import time

class CustomTextAgent:

    AnalyzeSentiment = 'sentiment'
    KeyPhrases = 'keyphrases'
    Entities = 'entities'
    DetectLanguage = 'detectlanguage' 
    def __init__(self, endpoint, key) -> None:
        self.endpoint = endpoint
        self.key = key
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-type': 'application/json',
        }

    def get_keyphrases(self, documents):
        url = self.endpoint+'/text/analytics/v3.1/keyPhrases'
        resp = requests.post(url, headers=self.headers,
                             json={'documents': documents})
        self.save_response(resp.json(), 'get-keyphrases')
        return resp.json()

    def analyse_sentiment(self, documents):
        url = self.endpoint + '/text/analytics/v3.1/sentiment'
        resp = requests.post(
            url, params={'opinionMining': 'true'}, headers=self.headers, json={'documents': documents})
        self.save_response(resp.json(), 'analyse-sentiment')
        return resp.json()

    def get_entities(self, documents):
        url = self.endpoint + '/text/analytics/v3.1/entities/recognition/general'
        resp = requests.post(
            url, headers=self.headers, json={'documents': documents})
        self.save_response(resp.json(), 'get-entities')
        return resp.json()

    def detect_language(self, documents):
        url = self.endpoint + '/text/analytics/v3.1/languages'
        resp = requests.post(
            url, headers=self.headers, json={'documents': documents})
        self.save_response(resp.json(), 'detect-language')
        return resp.json()

    @staticmethod
    def parse(json_data, documents, type):
        if type == "sentiment":
            for i, res in enumerate(json_data['documents']):
                documents[i]["sentiment"] = res["sentiment"]
            return documents
        elif type == "entities":
            categories = set()
            for i, res in enumerate(json_data['documents']):
                entities = {'data':{}}
                data = {} 
                for entity in res['entities']:
                    if data.get(entity["category"]) is not None:
                        data[entity["category"]] += ","+entity["text"]
                    else:
                        data[entity["category"]] = entity["text"]
                    categories.add(entity["category"])
                entities['data'] = data
                documents[i]['entities'] = entities
            return documents,list(categories)
        elif type == "detectlanguage":
            for i, res in enumerate(json_data['documents']):
                print(res['detectedLanguage'])
        elif type == "keyphrases":
            for i, res in enumerate(json_data['documents']):
                documents[i]['keyphrases'] = ' '.join(res['keyPhrases'])
            return documents
        
    @staticmethod
    def save_response(response, fname):
        with open(f'/dbfs/mnt/claimsfiles/outputs/{fname}.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)    

class CustomOCRAgent:
    def __init__(self, endpoint, key, inputtype) -> None:
        self.endpoint = endpoint
        self.key = key
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-type': 'application/octet-stream' if inputtype=='stream' else 'application/json',
        }

    def read_document(self, streamdata = None, file_url = None):
        url = self.endpoint+'/vision/v3.2/read/analyze'
        if streamdata is not None:
            resp = requests.post(url, headers=self.headers, data = streamdata)
        else:
            resp = requests.post(url, headers=self.headers, json = {'url': file_url})
        operation_id = resp.headers['Operation-Location']
        while True:
            read_result = requests.get(operation_id, headers=self.headers)
            # print(read_result.json())
            if read_result.json()['status'] not in ['notStarted', 'running']:
                break
            time.sleep(1)
        self.save_response(read_result.json(), 'read-ocr')
        return read_result.json()

    @staticmethod
    def save_response(response, fname):
        with open(f'/dbfs/mnt/claimsfiles/outputs/{fname}.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)

    @staticmethod
    def parse(json_data, documents = []):
        finalData = []
        for i, res in enumerate(json_data['analyzeResult']['readResults']):
            textData = ' '.join([line['text'] for line in res['lines']])
            finalData.append(textData)
        return ' '.join(finalData)


class CustomTranslatorAgent:
    def __init__(self, endpoint, key, location) -> None:
        self.endpoint = endpoint
        self.key = key
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-type': 'application/json',
            'Ocp-Apim-Subscription-Region': location
        }

    def translate(self, documents):
        path = 'translate'
        url = self.endpoint + path
        params = {
            'api-version': '3.0',
            'to': ['en']
        }
        resp = requests.post(url, params=params,
                             headers=self.headers, json=documents)
        self.save_response(resp.json(), 'translator-resp')
        return resp.json()

    @staticmethod
    def save_response(response, fname):
        with open(f'/dbfs/mnt/claimsfiles/outputs/{fname}.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)

    @staticmethod
    def parse(json_data, documents):
        for i, res in enumerate(json_data):
            for data in res['translations']:
                documents[i]['text'] = data['text']
        return documents
