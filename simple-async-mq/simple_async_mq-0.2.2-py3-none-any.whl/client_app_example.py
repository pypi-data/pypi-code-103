from client_app import receive_msg, connect, publish_msg

@receive_msg(topic='topic1')
def handle(data):
    print("TEST1:", data)

@receive_msg(topic='topic3')
def handle(data):
    print("TEST2:", data)

connect(
    host='localhost',
    port='10000',
    # topic='topic1',
    topics=[('topic1', 'json'), ('topic3', 'json')],
    output_format='json'
)
