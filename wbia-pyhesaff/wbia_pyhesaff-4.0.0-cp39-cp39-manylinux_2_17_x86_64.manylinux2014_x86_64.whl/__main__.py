# -*- coding: utf-8 -*-
def main():  # nocover
    import pyhesaff

    print('Looks like the imports worked')
    print('pyhesaff = {!r}'.format(pyhesaff))
    print('pyhesaff.__file__ = {!r}'.format(pyhesaff.__file__))
    print('pyhesaff.__version__ = {!r}'.format(pyhesaff.__version__))

    print('pyhesaff.HESAFF_CLIB = {!r}'.format(pyhesaff.HESAFF_CLIB))
    print('pyhesaff.__LIB_FPATH__ = {!r}'.format(pyhesaff.__LIB_FPATH__))


if __name__ == '__main__':
    """
    CommandLine:
       python -m pyhesaff
    """
    main()
