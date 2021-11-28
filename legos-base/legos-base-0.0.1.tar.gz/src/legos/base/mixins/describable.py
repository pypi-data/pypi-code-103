class DescriptionMixin(object):
    """DescriptionMixin class adds _description attribute to the subclass and
    also adds description property to get and set the description attribute.
    """

    def __init__(self, description=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._description = description

    @property
    def description(self):
        """Returns the description attribute set on the instance.
        Also sets the description attribute on the instance.
        """
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
