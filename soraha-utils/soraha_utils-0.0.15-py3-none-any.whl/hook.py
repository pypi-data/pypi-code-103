from typing import Any, Callable


class hook_manager:
    def __init__(self) -> None:
        """预设解析函数与终止函数,以免报错Not Found"""
        self.parser_func = None
        self.ending_func = None

    def parser(self, func: Callable) -> Callable:
        """记录解析函数,用作装饰器时记得接受一个字典用作在解析,主以及终止函数中相互传递

        Args:
            func (Callable): 用户编写的解析函数

        Returns:
            Callable: 返回解析函数
        """
        self.parser_func = func
        return func

    def runner(self, func: Callable) -> Callable:
        """将main函数切换为run函数

        Args:
            func (Callable): 用户编写的main函数

        Returns:
            Callable: run函数
        """

        def run(*arg, **kw) -> dict[str, Any]:
            """主函数,检测是否定义了解析函数与终止函数,并且顺序执行

            Returns:
                dict[str, Any]: 记录三个函数各自的返回,以及在函数中传递的字典states
            """
            self.states = {}
            if self.parser_func:
                parser_res = self.parser_func(self.states)
            main_res = self.func(self.states, *arg, **kw)
            if self.ending_func:
                ed_res = self.ending_func(self.states)
            return {
                "parser_res": parser_res,
                "main_res": main_res,
                "ed_res": ed_res,
                "states": self.states,
            }

        self.func = func
        return run

    def end_func(self, func: Callable) -> Callable:
        """记录终止函数,用作装饰器时记得接受一个字典用作在解析,主以及终止函数中相互传递

        Args:
            func (Callable): 用户编写的终止函数

        Returns:
            Callable: 返回终止函数
        """
        self.ending_func = func
        return func

    @staticmethod
    def with_hook() -> Callable:
        """唯一且应该调用的接口,用于注册一个hook函数,在调用时会传递一个字典`hook_manager.states`用于几个函数间的交互具体示例如下
        ```
        @hook_manager.with_hook()
        def test(session):
            # 在调用argp后会调用test
            # session = {'start'='first'}
            session['main'] = 'second'
        @test.arg_parser()
        def argp(session):
            # 这个函数会最先被调用
            session['start'] = 'first'
        @test.ending
        def endg(session):
            # 这个函数会在完成test后调用
            # 在调用argp后会调用test
            # session = {'start'='first','main':'second'}
            session['last'] = 'third'
        ```

        Returns:
            Callable: 返回deco函数,请注意！！！在如上示例的运行后,`test`函数实际上是`hook_manager.run`函数
        """

        def deco(func: Callable) -> Callable:
            """真正的去注册一个hook函数

            Args:
                func (Callable): 用户编写的函数

            Returns:
                Callable: hook_manager.run
            """
            hk = hook_manager()
            func = hk.runner(func)
            func.arg_parser = hk.parser
            func.ending = hk.end_func
            return func

        return deco
