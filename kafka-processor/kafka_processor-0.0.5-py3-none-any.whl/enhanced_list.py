
class EnhancedList(list):
    """a child of python built-in list with support of getting the last access item index"""

    def __init__(self, *args, **kwargs):
        super(EnhancedList, self).__init__(*args, **kwargs)
        self.last_accessed_index = None

    def __getitem__(self, key):
        """
        get item from the current instance by key
        :param key: key to get
        :return: value associated with the key
        """

        self.last_accessed_index = key

        value = super(EnhancedList, self).__getitem__(key)
        return value

    def __iter__(self, *args, **kwargs):
        """
        iterate on the current instance
        :return: all items one at a time
        """

        idx = 0
        for value in super(EnhancedList, self).__iter__(*args, **kwargs):
            self.last_accessed_index = idx
            yield value
            idx += 1
