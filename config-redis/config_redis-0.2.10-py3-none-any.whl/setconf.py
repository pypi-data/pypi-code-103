from configredis.setredis import SetRedis
from json import dumps, loads
from datetime import datetime
import sys
import logging
import os
import socket
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
redis = SetRedis()


class Tools:
    @classmethod
    def host_ip(cls, hostname: str):
        return socket.gethostbyname(hostname)

    @classmethod
    def project_name(cls, path=os.getcwd(), dirs=(".git",), default=None):
        """
        get current project name.
        :param path: scripts path
        :param dirs: save rule e.g: catch git
        :param default: if set default then save to the default absolute path
        :return: project root directory name
        """
        prev, path = None, os.path.abspath(path)
        while prev != path:
            if any(os.path.isdir(os.path.join(path, d)) for d in dirs):
                return path.split('/')[-1]
            prev, path = path, os.path.abspath(os.path.join(path, os.pardir))
        return default

    @classmethod
    def lookup_redis_proj_config(cls, proj_name=None):
        """
        lookup project config on redis.
        :param proj_name: project name which lookup from redis.
        """
        proj_name = proj_name or cls.project_name()
        return redis.getconf(proj_name)

    @classmethod
    def lookup_proj_config(cls, env=None, replace_domain=''):
        """
        lookup current project config.
        """
        conf_mapping_ = SetConfig.local_mapping_ or SetConfig.redis_mapping_
        return SetConfig.with_domain(conf_mapping_, replace_domain, env)


class ConfigUpdate:
    project_name_ = Tools.project_name()
    local_mapping_ = {}
    redis_mapping_ = Tools.lookup_redis_proj_config()

    @classmethod
    def upsert_config_to_redis(cls, mapping=None, notify=True):
        """
        insert or update current config to redis.
        """
        redis.set_conf(cls.project_name_, mapping=mapping or cls.local_mapping_, notify=False)
        logger.info(f" {cls.project_name_}'s config has been written to redis.") if notify else None

    @classmethod
    def upsert_field_to_redis(cls, env='default', notify=True, **kwargs):
        conf_mapping_ = cls.local_mapping_ or cls.redis_mapping_
        conf_mapping_[env] = {**conf_mapping_[env], **kwargs}
        redis.set_conf(cls.project_name_, mapping=conf_mapping_, notify=False)
        logger.info(f" {cls.project_name_}'s {env} config fileds has been written to redis.") if notify else None

    @classmethod
    def with_domain(cls, configs, replace_domain='', env=None):
        configs = dumps(configs)
        conf = loads(cls.__change_host(configs, replace_domain) if replace_domain else configs)
        return {**conf.get('default', {}), **conf.get(env)} if env else conf

    @classmethod
    def __change_host(cls, conf, domain: str):
        pattern = r'[\w\.]+' + domain.replace('.', r'\.')
        conf, pattern = conf, re.compile(r'' + pattern)
        n_d = {i: Tools.host_ip(i) for i in pattern.findall(conf)}
        for k, v in n_d.items():
            conf = conf.replace(k, v)
        return conf

    class ConfigArgs:
        """
        get config args value from redis.
        """

        def __getitem__(self, env):
            """
            sample:
            :param env: name is 'dev'
            :return: dict e.g: {'disk_name': 'TenTBc'}
            """
            return Tools.lookup_redis_proj_config().get(env, {})


class SetConfig(ConfigUpdate):
    __init_conf = ['default', 'dev', 'pro']

    @classmethod
    def defaultconfig(cls, **mapping):
        """
        set default env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('default', **mapping)

    @classmethod
    def devconfig(cls, **mapping):
        """
        set development env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('dev', **mapping)

    @classmethod
    def proconfig(cls, **mapping):
        """
        Set production env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('pro', **mapping)

    @classmethod
    def envconfig(cls, env_: str, **mapping):
        """
        Set production env args.
        need import this func to your config document.
        :param env_: env name
        :param mapping: dict
        """
        cls.local_mapping_[env_] = mapping

    @classmethod
    def configs(cls, replace_domain: str = None, on_redis=True):
        """
        get config info according env args. [defult/dev/pro]
        need import this func to your END of config document.
        :return: env config info as dict.
        """
        env = sys.argv[-1].lower()
        if not cls.local_mapping_:
            logger.warning(' Not catch local project config, will use Redis project config.')
        conf_mapping_ = cls.local_mapping_ or cls.redis_mapping_
        if env not in conf_mapping_:
            logger.warning(' Not catch env args or defultconfig not setup. e.g: python sample.py dev|pro')
            logger.warning(' Will start under dev env? exit: ctrl+c')
            env = 'dev'
        logger.info(f' Current env is {env}\n')
        if on_redis:
            cls.upsert_config_to_redis(cls.local_mapping_, notify=False)
        return cls.with_domain(conf_mapping_, replace_domain, env)

    @classmethod
    def delconfs(cls, proj_name=None):
        """
        delete concent from name or key.
        :param proj_name: proj_name
        """
        proj_name = proj_name or cls.project_name_
        confs, res = cls.getconfs(proj_name, score_cast_func=int), 0
        del_items, choose = cls.__choose_items(confs)
        if '0' in choose:
            res = redis.redis.delete(proj_name)
        elif del_items:
            res = redis.redis.zrem(proj_name, *del_items)
        if res:
            logger.info(' Redis configs has been deleted.')

    @classmethod
    def getconfs(cls, proj_name=None, score_cast_func=None):
        proj_name = proj_name or cls.project_name_
        f_score = score_cast_func or cls.__f_score
        return {str(i[1]): i[0] for i in redis.redis.zscan_iter(proj_name, score_cast_func=f_score)}

    @classmethod
    def print_config(cls, proj_name=None):
        proj_name = proj_name or cls.project_name_
        info = ''
        confs = cls.getconfs(proj_name, score_cast_func=int)
        print_items = cls.__choose_items(confs, stamp=True, reverse=True)[0]
        for i in print_items:
            info += f"\n\n>>{cls.__f_score(i)}<<\n\n" + "\n\n".join(
                [cls.__f_env_key(k) + cls.__f_env_conf(v) for k, v in loads(confs[i]).items()]) + '\n'
        print(f"{info}")

    @classmethod
    def indent(cls, num):
        return ''.rjust(num, ' ')

    @classmethod
    def __choose_items(cls, confs, stamp=False, reverse=False):
        sore_keys = list(confs.keys())
        sore_keys.sort(reverse=reverse)
        p_conf = "\n".join(["0: All", *[f"{k + 1}: {cls.__f_score(v)} -> {confs[v]}"
                                        for k, v in enumerate(sore_keys)]])
        print(p_conf)
        choose = input('Enter index num which config choosed (split with ","):').replace(' ', '').split(',')
        return [sore_keys[i] if stamp else confs[sore_keys[i]] for i in range(len(sore_keys)) if str(i + 1) in choose
                ], choose

    @classmethod
    def __f_env_key(cls, env_key):
        return (f"SetConfig.{env_key}config(\n" if env_key in cls.__init_conf else
                f"SetConfig.envconfig(\n{cls.indent(4)}'{env_key}',\n")

    @classmethod
    def __f_env_conf(cls, env_conf: dict):
        return f'{cls.indent(4)}' + f'{cls.indent(4)}'.join(
            [f'{k}="{v}",\n' if isinstance(v, str) else f'{k}={v},\n' for k, v in env_conf.items()]) + ")"

    @classmethod
    def __f_score(cls, stamp):
        return f"{datetime.fromtimestamp(int(stamp))} ({stamp})"
