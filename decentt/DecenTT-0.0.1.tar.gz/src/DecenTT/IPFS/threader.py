import threading


class ThreadDecorator:
    @classmethod
    def thread(cls, function):  #
        def inner_thread(*args):
            fun_thread = threading.Thread(target=function, args=args)
            fun_thread.start()
            return fun_thread

        return inner_thread
