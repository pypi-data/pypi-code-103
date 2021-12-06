# 安装SDK pip install git+https://github.com/panyunsuo/AlgorithmicMicroserviceSDK.git
# SDK使用文档 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/ffdma4

from algorithm_mic_sdk.algorithms.photo_to_cartoon import PhotoToCartoon
from algorithm_mic_sdk.auth import AuthInfo
from algorithm_mic_sdk.tools import FileInfo

host = 'http://nyasu.leqi.us:17013'  # 算法host地址
user_name = 'wangxiang'
password = 'e5c59b48-f975-11eb-b534-0242ac110003'


def run(filename, style='Disney_crown', enlargement_factor=3):
    """
    获取人脸特征点
    @param filename: 文件名
    @param style: 风格
    @param enlargement_factor:放大倍数
    @return:
    """
    file_info = FileInfo.for_file_bytes(open(filename, 'rb').read())  # 创建文件对象
    auth_info = AuthInfo(host=host, user_name=user_name, extranet=True, password=password,
                         gateway_cache=False)  # 初始化验证信息
    fluorescent_pen_recognition = PhotoToCartoon(auth_info, file_info, style=style,
                                                 enlargement_factor=enlargement_factor)  # 创建算法对象
    resp = fluorescent_pen_recognition.synchronous_request()  # 同步请求算法
    # print(fluorescent_pen_recognition.get_file_url(resp.result['result_im_oss_name']))
    return resp.result['facial_points']


if __name__ == '__main__':
    print(run('src/漫画/1.png'))
