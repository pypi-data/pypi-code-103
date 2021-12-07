# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: Sep 16, 2018
# Modified: Jun 12, 2020

from siki.basics import Exceptions
import threading


class Queue:

    def __init__(self):
        self.queue = list()
        self.index = 0
        self.lock = threading.Lock()

    def enqueue(self, data):
        """
        Adding element to queue
        """
        try:
            self.lock.acquire()

            if data not in self.queue:
                self.queue.insert(0, data)
                return True
            return False

        finally:
            self.lock.release()

    def dequeue(self):
        """
        Deleting element from queue
        """
        try:
            self.lock.acquire()

            if len(self.queue) > 0:
                return self.queue.pop()
            else:
                raise Exceptions.EmptyCollectionElementException("Cannot dequeue an empty queue")
        finally:
            self.lock.release()

    def size(self):
        """
        Getting the size of queue
        """
        return len(self.queue)

    def merge(self, queue):
        """
        merge two queues into one
        """
        try:
            self.lock.acquire()

            if type(queue) is list or type(queue) is Queue:
                for item in queue:
                    self.enqueue(item)
            else:
                raise Exceptions.InvalidParamException("cannot merge a non-list or non-queue type")
        finally:
            self.lock.release()

    def empty(self):
        try:
            self.lock.acquire()
            del self.queue
            self.queue = list()

        finally:
            self.lock.release()

    def is_empty(self):
        return len(self.queue) <= 0

    def __str__(self):
        return str(self.queue)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        try:
            return self.queue[self.index]
        except IndexError as e:
            raise StopIteration
        finally:
            self.index += 1

    def __len__(self):
        return len(self.queue)
