import os, json
from google.cloud import pubsub_v1

def ps_publish(json_request, topic_name):
    project = os.environ['GCP_PROJECT']
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    string_request = json.dumps(json_request).encode()
    future = publisher.publish(topic_path, data=string_request).result()
    return ('200')
