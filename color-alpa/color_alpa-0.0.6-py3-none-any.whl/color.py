'''
Color text usning ANSI escape code
https://en.wikipedia.org/wiki/ANSI_escape_code

Copyright (c) 2020 Albert Pang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


class Color(object):
    '''A whole bunch of static methods to color texting using ANSI escape sequence
    '''
    BLACK = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    ENDC = '\033[0m'

    def __init__(self):
        pass

    @staticmethod
    def bold(text):
        '''bold text'''
        return Color.BOLD + text + Color.ENDC

    @staticmethod
    def underline(text):
        '''underline text'''
        return Color.UNDERLINE + text + Color.ENDC

    @staticmethod
    def black(text):
        '''black color'''
        return Color.BLACK + text + Color.ENDC

    @staticmethod
    def red(text):
        '''red color'''
        return Color.RED + text + Color.ENDC

    @staticmethod
    def green(text):
        '''green color'''
        return Color.GREEN + text + Color.ENDC

    @staticmethod
    def yellow(text):
        '''yellow color'''
        return Color.YELLOW + text + Color.ENDC

    @staticmethod
    def blue(text):
        '''blue color'''
        return Color.BLUE + text + Color.ENDC

    @staticmethod
    def magenta(text):
        '''magenta color'''
        return Color.MAGENTA + text + Color.ENDC

    @staticmethod
    def cyan(text):
        '''cyan color'''
        return Color.CYAN + text + Color.ENDC


class Colour(Color):
    pass


def main():
    '''main function'''
    pass


if __name__ == '__main__':
    main()
