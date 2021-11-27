# 初始化基类
import logging
import traceback

from django.conf import settings
logger = logging.getLogger(__name__)


class CoreChecker:
    """
    使用方法：继承此类，重写 run方法，在 run 中调用 save 进行数据初始化
    """
    plugin_name = 'default'
    requirements_list = []

    def requrement(self):
        import os
        from pathlib import Path
        requirement = os.path.join(Path(__file__).resolve(strict=True), "requirements.txt")
        logger.info(f'检查插件依赖环境中,插件:{self.plugin_name}')
        lack_list = []
        for req in self.requirements_list:
            try:
                exec(f'import {req}')
            except ImportError:
                lack_list.append(req)
        if len(lack_list) > 0:
            logger.error(f'依赖环境不满足，缺少:{",".join(lack_list)}')
        else:
            logger.info(f'依赖环境满足')

        logger.info(f'{self.plugin_name}:依赖环境文件{"存在" if os.path.exists(requirement) else "不存在"}')
        if os.path.exists(requirement):
            logger.error(f'正在安装依赖文件:{self.plugin_name}')
            try:
                os.system(f'pip install -r {requirement}')
            except Exception:
                traceback.print_exc()
        else:
            logger.error(f'依赖环境文件不存在:{self.plugin_name}')


    def _check(self):
        self.requrement()
        self.check()

    def check(self):
        pass
        # self.migrate()
