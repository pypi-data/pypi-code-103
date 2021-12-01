from abc import ABC, abstractmethod
from collections import deque
import multiprocessing
from multiprocessing import Queue as MQueue

class Queue(ABC):
    '''!
        Generic queue for communication between stages.
    '''

    def __init__(self, max_size):
        self.max_size = max_size
    
    @abstractmethod
    def get(self):
        '''!
            Returns the first element of the queue.
            Returns:
                @returns the first element of the queue
        '''
        ...
    
    def pop(self):
        '''!
            Returns the first element of the queue.
            Returns:
                @returns the first element of the queue
        '''
        
        return self.get()
    
    @abstractmethod
    def insert(self, value):
        '''!
            Insert a value in the end of the queue.
            Parameters:
                @param value - the value
        '''

        ...
    
    @abstractmethod
    def empty(self):
        '''!
            See if the queue is empty.
            Returns:
                @returns True if empty
        '''

        ...

    @abstractmethod
    def full(self):
        '''!
            See if the queue if full
            Returns:
                @returns True if full
        '''

        ...

class SimpleQueue(Queue):
    '''!
        A simple queue. Must not be used for multiprocessing
        Uses collections.deque for implement the queue
    '''

    def __init__(self, max_size=100):
        super().__init__(max_size)
        self.queue = deque(maxlen=max_size)
    
    def get(self):
        '''!
            Returns the first element of the queue.
            Returns:
                @returns the first element of the queue
        '''

        return self.queue.popleft()

    def insert(self, value):
        '''!
            Insert a value in the end of the queue.
            Parameters:
                @param value - the value
        '''

        self.queue.append(value)
    
    def empty(self):
        '''!
            See if the queue is empty.
            Returns:
                @returns True if empty
        '''

        if len(self.queue) > 0:
            return False
        return True

    def full(self):
        '''!
            See if the queue if full
            Returns:
                @returns True if full
        '''

        if len(self.queue) >= self.max_size:
            return True
        return False

class ProcessQueue(Queue):
    '''!
        Queue for using in multiprocessing.
        For single process pipeline, SimpleQueue is better
        Uses multiprocessing.queue for implement the queue
    '''


    def __init__(self, max_size=100):
        super().__init__(max_size)
        
        
        self.queue = MQueue(maxsize=max_size)


    def get(self):
        '''!
            Returns the first element of the queue.
            Returns:
                @returns the first element of the queue
        '''

        return self.queue.get()
    
    def insert(self, value):
        '''!
            Insert a value in the end of the queue.
            Parameters:
                @param value - the value
        '''

        self.queue.put(value)
    
    def empty(self):
        '''!
            See if the queue is empty.
            Returns:
                @returns True if empty
        '''

        return self.queue.empty()
    
    def full(self):
        '''!
            See if the queue if full
            Returns:
                @returns True if full
        '''

        return self.queue.full()