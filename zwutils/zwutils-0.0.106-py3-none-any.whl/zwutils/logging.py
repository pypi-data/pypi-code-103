import io

class Stream(object):

    def __init__(self, stream=None):
        if stream is None:
            stream = io.StringIO()
        self.stream = stream
        self.encoding = getattr(self.stream, 'encoding', None) or 'utf-8'

    def write(self, text):
        self._prints(text, end='')

    def flush(self):
        self.stream.flush()

    def prints(self, level, *args, **kwargs):
        self._prints(*args, **kwargs)

    def _prints(self, *args, **kwargs):
        prints(*args, **kwargs, file=self.stream)




