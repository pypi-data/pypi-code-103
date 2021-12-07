class KafkaServer:
    # @match_typing
    def __init__(self,
                 address: str,
                 port: int
                 ):
        self.address = address
        self.port = port

    def __str__(self):
        return f'{self.address}:{self.port}'


class KafkaTopic:
    # @match_typing
    def __init__(self,
                 server: KafkaServer,
                 topic_id: str
                 ):
        self.server = server
        self.topic_id = topic_id

