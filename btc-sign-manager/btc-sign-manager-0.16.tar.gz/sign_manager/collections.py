class SignedObjectType:
    """
    A collection of objects types for sign
    """

    XML = 'xml'
    SIMPLE_FILE = 'base64'
    BIG_FILE = 'base64_hash'

    ITEMS = (
        XML,
        SIMPLE_FILE,
        BIG_FILE
    )

    CHOICES = (
        (XML, 'xml'),
        (SIMPLE_FILE, 'base64'),
        (BIG_FILE, 'base64_hash'),
    )
