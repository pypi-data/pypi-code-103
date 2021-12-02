from configredis import SetConfig, Tools, SetRedis


con = SetConfig.ConfigArgs()

SetConfig.defaultconfig(
    c_env='default',
    disk_name='TenD'
)

SetConfig.devconfig(
    c_env='dev',
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    r_flow={'host': Tools.host_ip('httpbin.org'), 'port': 7000, 'db': 0, "cluster": True},
    r_flow1={'host': 'httpbin.org', 'port': 7000, 'db': 0, "cluster": True}
)

SetConfig.proconfig(
    c_env='pro',
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    disk_name="TenB"
)

SetConfig.envconfig(
    'custom_env',
    c_env='custom_env'
)

config = SetConfig.configs('bin.org')  # 如果明文配置env，会以明文配置优先，如果配置文件删除明文配置，则会查找redis最新配置，SetConfig.configs会自动把明文配置持久化到redis  # noqa


if __name__ == '__main__':
    print(config)  # 获得当前env的配置
    # print(SetConfig.getconfs())  # 查看redis中项目目前所有版本配置
    # SetConfig.print_config()  # 罗列项目所有版本的配置信息，并根据index打印相关配置，方便复制到配置文件, 顺序从新到旧
    # print(con['custom_env'])  # 根据env查看redis储存的最新配置
    # SetConfig.upsert_field_to_redis('custom_env', disk_name='TenC')  # 明文配置删除的情况下，给redis中的最新配置增加字段，不要跟明文配置同时使用，会导致redis版本错乱  # noqa
    # print(Tools.lookup_redis_proj_config())  # 显示redis存储的最新配置
    # print(Tools.lookup_proj_config(replace_domain='bin.org'))  # 显示当前所有env配置，明文优先于redis配置
    # print(SetRedis().getkeys())  # 查看redis所有的项目名称
    # SetConfig.delconfs()  # 罗列项目所有版本的配置信息，并根据index删除相关配置, 顺序从旧到新
