import time
import datetime
import random
from decimal import Decimal

import requests
from . import tool


class Parse():

    def convert_uppercase(self, string):
        """
        将字符串转换成大写
        """
        return string.upper()

    @property
    def randomNum(self):
        '''
        '''
        return random.randint(0, 9)

    @property
    def not_repeat_string(self):
        """
        获取不重复字符串
        @return:
        """
        return '{}_{}_{}'.format(''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 4)),
                              ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 4)),
                              str(float(time.time())))

    @property
    def generate_identity_card(self):
        '''
            创建身份证
        '''
        return tool.IdNumber.generate_myid()
    
    def create_social_credit(self):
        '''
        生成社会信用代码
        @return:
        '''
        return tool.IdNumber().create_social_credit()
    
    def get_identity_card(self, age=None):
        '''
            获取一个身份证
            age: 年龄
        '''
        return tool.IdNumber().get_identity_card(age)

    def get_bank_card_number(self):
        '''
            获取一个银行卡
        '''
        return tool.GetBankCardNumber().get_bank_card_number()

    def get_card_no_bank(self, cardNo):
        '''
        根据银行卡获取对应银行,未查找到返回CMB招商银行
        @param cardNo:银行卡
        @return:
        '''
        url = 'https://ccdcapi.alipay.com/validateAndCacheCardInfo.json?cardNo={}&cardBinCheck=true'.format(cardNo)
        response = requests.get(url).json()
        if 'bank' in list(response.keys()):
            return response['bank']
        else:
            return 'CMB'
    
    def get_age_card(self, age=None):
        if age == '' and age is None:
            age = None
        return tool.IdNumber.generate_myid(age)
    
    @property
    def car_number(self):
        '''
            获取一个车牌号
        '''
        return tool.IdNumber.car_number()
    
    @property
    def random_name(self):
        '''
            获取一个名字
        '''
        return tool.IdNumber.random_name()

    @classmethod
    def generate_phone(self):
        prefix = [
            '130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
            '145', '147', '149', '150', '151', '152', '153', '155', '156', '157',
            '158', '159', '165', '171', '172', '173', '174', '175', '176', '177',
            '178', '180', '181', '182', '183', '184', '185', '186', '187', '188',
            '189', '191'
        ]

        # 随机取一个手机号前缀
        pos = random.randint(0, len(prefix) - 1)
        # 随机生成后8位数字
        suffix = str(int(time.time() * 1000))[-8:]
        # 拼接返回11位手机号
        return prefix[pos] + suffix

    @classmethod
    def current_subtle_unix(self):
        # 当前微妙时间
        return int(time.time()*1000)
    
    def generate_email(self, domain='163.com'):
        """
        获取一个随机邮箱号
        :param domain:域名，默认163邮箱
        :return:
        """
        random_str = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', random.randint(6,20)))
        return 'test_{}@{}'.format(random_str, domain)
    
    @property
    @classmethod
    def current_unix(self):
        # 当前时间
        return int(time.time())

    @property
    def current_subtle_unix_str(self):
        # 当前微妙时间
        # 等待1微妙防止重复
        time.sleep(0.001)
        return str(int(float(time.time())*100000))

    @property
    def current_subtle_str_unix(self):
        # 当前微妙时间（字符串类型）
        # 等待1微妙防止重复
        time.sleep(0.001)
        return str(int(float(time.time())*1000))
    
    def get_age_unix(self, num, is_positive=False):
        '''
            获取一个年龄超过n岁的时间
            is_positive 为false，取当前时间往前n年的时间
            is_positive 为true，取当前时间往后n年的时间
        '''
        num = int(num)
        _format = "%Y-%m-%d"
        today = datetime.date.today().strftime(_format)
        current_date = today.split()[0]
        y = current_date.split('-')[0]
        if is_positive is False:
            age = '{}-{}'.format(str(int(y)-num), '-'.join(current_date.split('-')[1:]))
        else:
            age = '{}-{}'.format(str(int(y)+num), '-'.join(current_date.split('-')[1:]))
        self.logger.debug(age)
        return int(time.mktime(time.strptime(age, _format)))
    
    @property
    def yesterday_start_unix(self):
        # 昨天开始时间
        return self.get_start_unix(1)

    def get_start_unix(self, day):
        '''
        获取n天前的开始时间
        @param day: n，提前n天
        @return:unix时间戳
        '''
        return int(time.mktime(time.strptime(str(datetime.date.today() - datetime.timedelta(days=int(day))), '%Y-%m-%d')))


    def get_start_date(self, day, format='%Y-%m-%d %H:%M:%S'):
        '''
        获取n天前的开始时间
        @param day: n，提前n天
        @param format: 时间格式
        @return:字符串时间
        '''
        return self.strp_unix_by_date(self.get_start_unix(day), format)

    def get_end_unix(self, day):
        '''
        获取n天前的结束时间
        @param day: n，提前n天
        @return:unix时间戳
        '''
        return self.get_start_unix(int(day)-1)-1


    def get_end_date(self, day, format='%Y-%m-%d %H:%M:%S'):
        '''
        获取n天前的结束时间
        @param day: n，提前n天
        @param format: 时间格式
        @return:字符串时间
        '''
        return self.strp_unix_by_date(self.get_end_unix(day), format)

    @property
    def yesterday_end_unix(self):
        # 昨天结束时间
        return int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))) - 1
    
    @property
    def today_start_unix(self):
        # 今天开始时间
        return int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d')))
    
    @property
    def sign_expire_time(self):
        '''
            特殊场景,签约时间，当前时间-20分钟
        '''
        return int(time.time()) - 20*60
    
    @property
    def today_end_unix(self):
        # 今天结束时间
        return int(time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d'))) - 1
    
    @property
    def tomorrow_start_unix(self):
        # 明天开始时间戳
        return int(time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=1)), '%Y-%m-%d')))

    @property
    def tomorrow_end_unix(self):
        # 明天结束时间
        return int(time.mktime(time.strptime(str(datetime.date.today() + datetime.timedelta(days=2)), '%Y-%m-%d'))) - 1

    def strp_date_by_unix(self, date, format='%Y-%m-%d'):
        '''
        将字符串时间或datetime时间转换为unix时间
        @param date:字符串时间
        @param format:字符串时间格式，默认%Y-%m-%d,其他参考值%Y-%m-%d %H:%M:%S.%f
        @return:
        '''
        if type(date) == str:
            date = datetime.datetime.strptime(date, format)
        if format == '%Y-%m-%d %H:%M:%S.%f':
            return time.mktime(date.timetuple())*1e3 + date.microsecond/1e3
        return time.mktime(date.timetuple())

    def current_local_date_str(self, format='%Y-%m-%d %H:%M:%S'):
        '''
        获取当前时间
        @param format: 返回格式，默认%Y-%m-%d %H:%M:%S
        @return:
        '''
        return datetime.datetime.now().strftime(format)

    def strp_unix_by_date(self, date, format='%Y-%m-%d %H:%M:%S'):
        '''
        将unix时间转换为字符串时间
        @param date:unix时间
        @param format:字符串时间格式，默认%Y-%m-%d,其他参考值%Y-%m-%d %H:%M:%S
        @return:
        '''
        # value为传入的值为时间戳(整形)，如：1332888820
        value = time.localtime(date)
        return time.strftime(format, value)

    def _sum(self, *args):
        '''
        求和，此函数解决float相加或相减
        @param args:
        @return:
        '''
        total = 0
        for i in args:
            total = Decimal(str(float(total))) + Decimal(str(float(i)))
        return float(total)
