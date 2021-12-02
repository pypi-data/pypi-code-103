"""Superclasses for input data files.
"""


# ------------------------------------------------ File exceptions
class FileReadError(RuntimeError):
    """Any type of exception during file read
    to be sub-classed for more specific variants depending on file format
    """


# -----------------------------------------------------------------------
class EmaRecord:  # **** might be just a dict, incl key 'subject' ? ***********
    """Container for a single EMA record
    """
    def __init__(self,
                 subject=None,
                 ema=None
                 ):
        """
        :param subject: string or any other immutable type
        :param ema: tuple of one or more tuples (cf, c_category)
        """
        self.subject = subject
        self.ema = ema

    def __repr__(self):
        return (self.__class__.__name__ + '(\n\t' +
                ',\n\t'.join(f'{key}={repr(v)}'
                             for (key, v) in vars(self).items()) +
                '\n\t)')


# ---------------------------------------------------------
def safe_file_path(p):
    """Ensure non-existing file path, to avoid over-writing,
    by adding a sequence number to the path stem
    :param p: file path
    :return: p_safe = similar file path with modified name
    """
    f_stem = p.stem
    f_suffix = p.suffix
    i = 0
    while p.exists():
        i += 1
        p = p.with_name(f_stem + f'-{i}.' + f_suffix)
    return p


# ---------------------------------------------------------
class EmaFile:
    """Superclass for any container of EMA records
    from one or more Subjects, participating in an EMA study with
    one or more nominal Scenarios, and zero or more ordinal Attributes,
    accessed by an iterator yielding EmaRecord instances.

    This super-class is used mainly for READING a data file.

    Sub-classes must be defined for each specific file format.
    Sub-classes MUST define an __iter__ method, yielding EmaRecord instances
    """
    def __init__(self, file_path):
        """
        :param file_path: Path instance for READING, or None.
            Another path may be defined in the save method.
        """
        self.file_path = file_path

    def __repr__(self):
        return (self.__class__.__name__ + '(\n\t' +
                ',\n\t'.join(f'{key}={repr(v)}'
                             for (key, v) in vars(self).items()) +
                '\n\t)')

    def __iter__(self):
        raise NotImplementedError

