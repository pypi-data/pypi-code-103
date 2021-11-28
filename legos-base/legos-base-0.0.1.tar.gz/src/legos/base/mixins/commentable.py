class CommentMixin(object):
    """CommentMixin adds comment attribute to the instance and also
    adds comment property to get and set this value.
    """

    def __init__(self, comment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comment = comment

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value
