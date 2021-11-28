from gaelib.db import model, properties

class Test(model.Model):
    """
        Test database
    """
    string1 = properties.StringProperty()
    string2 = properties.StringProperty()
    int1 = properties.IntegerProperty()
    float1 = properties.FloatProperty()
    bool1 = properties.BooleanProperty()
