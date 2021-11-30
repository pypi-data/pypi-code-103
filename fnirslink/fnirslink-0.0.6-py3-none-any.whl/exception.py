# -*- coding:utf8 -*-


class CustomError(Exception):
    def __init__(self, error_info):
        super(CustomError, self).__init__()  # 初始化父类
        self.error_info = error_info

    def __str__(self):
        return self.error_info


if __name__ == '__main__':
    try:
        raise CustomError('客户异常')
    except CustomError as e:
        print(e)
