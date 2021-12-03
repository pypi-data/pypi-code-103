__version__ = '0.1.1'


class str():

    # 除去两端空格

    def remove_space_twoends(s):
        return s.strip()

    # 删除所有空格

    def remove_space_all(s):
        return s.replace(" ", "")

    # 利用翻译删除指定空白字符

    def remove_white_type(s, sign=' \t\n\r\f\v'):
        return s.translate(None, sign)

    # 删除所有空白符

    def remove_white_all(s):
        return ''.join(s.split())

    # 空白字符替换成空格

    def white2space(s, sign=' \t\n\r\f\v'):
        return s.translate(' ', sign)

    # 多个空格保留一个

    def muti2single_space(s):
        return ' '.join(s.split())


def main():
    pass


if __name__ == '__main__':
    main()
