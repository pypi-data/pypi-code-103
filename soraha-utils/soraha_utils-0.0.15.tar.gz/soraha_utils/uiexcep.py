class Uio_MethodNotDefinded(Exception):
    pass


class Uitry_END_Trying(Exception):
    """适用于: 发生预期内错误需要结束uitry的时候
    使用: 可以import并直接抛出这个错误
          否则会继续正常执行,可能导致一些问题(重复执行某些不必要的函数)
    """
    pass