from .producer import Producer
from .consumer import Consumer



class Hybrid(Consumer, Producer):
    """Generic hybrid class of Producer and Consumer

    A consumer that can forward data to other consumers.

    This should rarely be used but can be used for data translation or other redirection.
    However, do not feel wary over implementing a hybrid worker;
    it's just that it can be counter-productive to the producer-consumer model,
    so implement with consideration. Keep out for recursive forwarding.
    """

    def __init__(self, consumers: list[Consumer]):
        Consumer.__init__(self)
        Producer.__init__(self, consumers)