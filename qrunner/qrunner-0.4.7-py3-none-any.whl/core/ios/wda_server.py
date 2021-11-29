import os
import subprocess
from qrunner.utils.log import logger


class WDAServer:
    def __init__(self, serial_no):
        self.serial_no = serial_no

    def launch_wda(self):
        logger.info(f'{self.serial_no} 开始启动wda服务')
        # 通过tidevice命令启动代理服务
        cmd = 'tidevice -u {0} xctest'.format(self.serial_no)
        self.p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            return_code = self.p.wait(5)
            raise subprocess.CalledProcessError(return_code, p)
        except Exception as e:
            code = e.__dict__.get('returncode')
            if code is None:
                logger.info(f'{self.serial_no} 启动wda服务成功.')
            else:
                logger.error(f'{self.serial_no} 启动wda服务失败: {e.__dict__}')

    def stop_wda(self):
        logger.info('\n停止wda服务')
        try:
            if os.name == 'nt':
                os.popen('taskkill /f /im tidevice.exe')
            else:
                self.p.kill()
        except Exception as e:
            logger.error(f'停止wda服务失败: {str(e)}')
        else:
            logger.info('停止wda服务成功')

