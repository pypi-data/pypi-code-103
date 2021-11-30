# -*- coding: utf-8 -*-

# 服务者名称[可包含多个服务]
SERVER_GATEWAY = "gateway"  # 网关服务
SERVER_ORDER_MANAGER = "order_manager"  # 订单管理
SERVER_TRADER = "trader"  # 交易进程
SERVER_QUANTS = "quants"  # 交易进程
SERVER_QUOTE_UT = "quote_ut"  # 行情-UT进程
SERVER_QUOTE_CTP = "quote_ctp"  # 行情-ctp进程
SERVER_MARKETDATA = "marketdata"  # 行情数据服务
SERVER_HQREALTIMEPUSH = "hqrealtimepush"  # 实时行情推送服务
SERVER_ACCOUNT = "account"  # 账户服务
SERVER_QUOTA = "quota"  # 行情查询服务

SERVER_DATA = "data"  # 数据(db)服务
SERVER_CONDITION = "condition"  # 条件服务
SERVER_NEST_CONDITION = "nest_condition"  # 嵌套条件单服务
SERVER_CONDITION_HTTP_GATEWAY = "condition_http_gateway"  # 条件单http服务网关
SERVER_ASSET = "asset"  # 资管服务
SERVER_ALGORITHM = "algorithm"  # 算法服务
SERVER_RISK = "risk"  # 风控服务
SERVER_GRID = "grid"  # 网格交易服务

SERVER_SIGNAL = "signal"  # 信号服务
SERVER_SIGNAL_CALC = "signal_calc"  # 信号计算服务

SERVER_STRATEGY = "strategy"  # 策略服务
SERVER_STRATEGY_CALC = "strategy_calc"  # 策略计算服务

SERVER_STOCKTHS = "transmid_stockths"  # 量化bus股票服务
SERVER_FORWARD = "forward"  # 转发服务
SERVER_WAREHOURSE = "warehourse"  # 分仓服务
SERVER_GRADECONDITION = "gradecondition"  # 分级条件单
SERVER_VERSION_MANAGER = "version_manager"  # 客户端版本管理
SERVER_CONFIGMANAGER = "configmanager"  # 配置管理模块
SERVER_MONITOR_CENTER = "monitor_center"  # 监控管理中心
SERVER_MONITOR_METRICS = "monitor_metrics"  # 监控指标转发中心
SERVER_MONITOR_RELAY = "monitor_relay"  # 监控指标转发中心/web请求中心

# 广播宏
TOPIC_MINDGO_SIGNAL = "topic.mindgo.signal"  # 信号推送
TOPIC_MONITOR = "topic.monitor"
TOPIC_TRADE = "topic.oms.trade"  # 成交推送
TOPIC_ORDER = "topic.oms.order"  # 委托推送
TOPIC_TRADE_FUTURES = "topic.trade.futures"  # 期货交易成交推送
TOPIC_ORDER_FUTURES = "topic.order.futures"  # 期货交易委托推送
TOPIC_TRADE_STOCK = "topic.trade.stock"  # 股票交易成交推送
TOPIC_ORDER_STOCK = "topic.order.stock"  # 股票交易委托推送

TOPIC_TRADE_CONDITION = "topic.trade.condition"  # 条件单交易成交推送
TOPIC_ORDER_CONDITION = "topic.order.condition"  # 条件单交易委托推送
TOPIC_TRIGGER_CONDITION = "topic.trigger.condition"  # 条件单触发推送
TOPIC_CHANGED_CONDITION = "topic.changed.condition"  # 条件单状态变更推送，成交，撤单，废单(已报，未报等中间状态不需要推送)

TOPIC_CHANGED_NEST_CONDITION = "topic.changed.nest_condition"  # 嵌套条件单变更推送

TOPIC_ORDER_POSITION = "topic.order.position"  # 仓位推送
TOPIC_ORDER_ACCOUNT_FUND = "topic.order.account.fund"  # 账户资金变动推送

TOPIC_QUOTE_TICK = "topic.quote.tick"  # 行情快照
TOPIC_QUOTE_TICK_FUTURES = "topic.quote.tick.futures"  # 期货快照
TOPIC_QUOTE_TICK_STOCK = "topic.quote.tick.stock"  # 股票快照

TOPIC_QUOTE_TRADE = "topic.quote.trade"  # 行情成交
TOPIC_QUOTE_ORDER = "topic.quote.order"  # 行情委托
TOPIC_QUOTE_ORDER_QUEUE = "topic.quote.order.queue"  # 行情委托队列

TOPIC_ORDER_CANCEL_FAILED = "topic.order.cancel.failed"  # 撤单失败推送
TOPIC_ACCOUNT_KILLED = "topic.account.killed"  # 账号被剔除事件
TOPIC_TRADE_ACCOUNT_KILLED = "topic.trade.account.killed"  # 资金账号被剔除事件
TOPIC_TRADE_ACCOUNT_LOGIN_NOTIFY = "topic.trade.account.login.notify"  # 资金账号登录事件通知
TOPIC_TRADE_ACCOUNT_LOGOUT_NOTIFY = "topic.trade.account.logout.notify"  # 资金账号全部登出事件通知
TOPIC_TRADE_ACCOUNT_LOGIN_FAILED_NOTIFY = "topic.trade.account.login_failed.notify"  # 资金账号登陆失败通知
TOPIC_QUERY_TRADING_ACCOUNT_TOKEN_NOTIFY = "topic.query.trading.account.token.notify"  # 查询监控中心令牌通知

TOPIC_SIGNAL_CLEANING = "topic.signal.cleaning"  # 信号清算事件
TOPIC_SIGNAL_STATUS_CHANGE = "topic.signal.status.change"  # 信号状态变更事件

TOPIC_SIGNAL_TRIGGER = "topic.signal.trigger"  # 信号触发事件
TOPIC_TRIGGER_PRICE_CHANGE = "topic.signal.trigger_price.change"  # 触发价变化事件

TOPIC_CLIENT_KILLED = "topic.client.killed"  # 客户端退出事件
TOPIC_CLIENT_CONNECTED = "topic.client.connected"  # 客户端连接事件
TOPIC_CLIENT_LOGIN = "topic.client.login"  # 用户登录事件
TOPIC_CLIENT_LOGOUT = "topic.client.logout"  # 用户登出事件
TOPIC_LOG_ELK = "topic.log.elk"  # 推送日志
TOPIC_GATAWAY_START = "topic.gateway.start"  # 网关启动事件

TOPIC_BANK_ACCOUNT_MONEY = "topic.bank.account.money"  # 银期查询余额通知
TOPIC_FROM_BANK_TO_FUTURE = "topic.from.bank.to.future"  # 银转期通知
TOPIC_FROM_FUTURE_TO_BANK = "topic.from.future.to.bank"  # 期转银通知

BROADCAST_GLOBAL = "broadcast.global"  # 全局广播标识

# 服务名称
SERVICE_TRADER_FUTURES = "rpc.trader.futures"  # 期货交易
SERVICE_TRADER_STOCK = "rpc.trader.stock"  # 股票交易
SERVICE_ORDER_MANAGER = "rpc.order.manager"  # 订单管理
SERVICE_TRADER_QUANTS = "rpc.trader.quants.service"  # 交易模块
SERVICE_CONDITION_GW = "rpc.condition.gw"  # 条件单网关服务

SERVICE_QUOTER_UT = "rpc.quoter.ut"  # 行情-ut
SERVICE_QUOTER_CTP = "rpc.quoter.ctp"  # 行情-ctp
SERVICE_MARKETDATA = "rpc.marketdata"  # 行情数据服务
SERVICE_HQREALTIMEPUSH = "rpc.hqrealtimepush"  # 实时行情推送服务
SERVICE_QUOTA = "rpc.quota"  # 行情咨询服务

SERVICE_ACCOUNT = "rpc.account"  # 账户
SERVICE_DATA = "rpc.data"  # 数据(db)服务
SERVICE_CONDITION = "rpc.condition"  # 条件服务(暂时无用)
SERVICE_CONDITION_FUTURE = "rpc.condition.futures"  # 期货条件单
SERVICE_NEST_CONDITION_FUTURE = "rpc.nest_condition.futures"  # 期货嵌套条件单
SERVICE_CONDITION_STOCK = "rpc.condition.stock"  # 股票条件单
SERVICE_ASSET = "rpc.asset"  # 资管服务
SERVICE_ALGORITHM = "rpc.algorithm"  # 算法服务
SERVICE_GRID = "rpc.grid"  # 网格交易服务
SERVICE_RISK = "rpc.risk"  # 风控服务

SERVICE_SIGNAL_MANAGER = "rpc.signal.manager"  # 信号服务管理
SERVICE_SIGNAL_CALC = "rpc.signal.calc"  # 信号计算服务

SERVICE_STRATEGY_CALC = "rpc.strategy.calc"  # 策略计算
SERVICE_STRATEGY_MANAGER = "rpc.strategy.manager"  # 策略服务

SERVICE_TRANSMID_STOCK = "rpc.transmid.service"  # 股票交易transmid
SERVICE_FORWARD = "rpc.forward"  # 转发服务
SERVICE_FORWARD_PRODUCT = "asset-product-api"  # 资管asset product服务
SERVICE_FORWARD_INSTITUTION = "asset-institution-api"  # 资管asset institution服务
SERVICE_WAREHOURSE = "rpc.warehourse"  # 分仓服务
SERVICE_GRADECONDITION = "rpc.gradecondition"  # "分级条件单"
SERVICE_VERSION_MANAGER = "rpc.version_manager"  # 客户端版本管理
SERVICE_CONFIGMANAGER = "rpc.configmanager"  # 配置管理模块
SERVICE_MONITORCENTER = "rpc.monitorcenter"  # 监控管理中心
SERVICE_MONITORCENTER_CONDITION = "rpc.monitorcenter.condition"  # 监控管理中心 条件单
SERVICE_MONITORMETRICS = "rpc.monitormetrics"  # 监控指标转发中心
SERVICE_MONITORRELAY = "rpc.monitorrelay"  # 监控指标转发中心
# 网关主动断线
SERVICE_GATEWAY = "gateway"  # 网关
METHOD_GATEWAY_ERROR = "gw_error"  # 网关错误事件

# 推送转发
SERVICE_PUSH_RELAY = "rpc.push.relay"  # 推送转发

# 分级条件单方法
METHOD_CREATE_GRADECONDITION = "create_gradecondition"  # 创建分级条件单
METHOD_CANCEL_GRADECONDITION = "cancel_gradecondition"  # 取消分级条件单
METHOD_DELETE_GRADECONDITION = "delete_gradecondition"  # 删除分级条件单
METHOD_PAUSE_GRADECONDITION = "pause_gradecondition"  # 暂停分级条件单
METHOD_ACTIVATE_GRADECONDITION = "activate_gradecondition"  # 激活分级条件单
METHOD_MODIFY_GRADECONDITION = "modify_gradecondition"  # 修改分级条件单
METHOD_QUERY_GRADECONDITION = "query_gradecondition"
METHOD_NEW_SUBJECT = "new_subject"  # 新增国债逆回购管理标的
METHOD_DELETE_SUBJECT = "delete_subject"  # 删除国债逆回购管理标的
METHOD_QUERY_SUBJECT = "query_subject"  # 查询国债逆回购管理标的
METHOD_MODIFY_SUBJECT = "modify_subject"  # 修改国债逆回购管理标的

# 分仓进程方法
METHOD_CREATE_WAREHOURSE = "create_warehourse"
# 创建分仓
METHOD_DELETE_WAREHOURSE = "delete_warehourse"
# 删除分仓
METHOD_QUERY_WAREHOURSE = "query_warehourse"
# 查询分仓
METHOD_MODIFY_WAREHOURSE = "modify_warehourse"
# 修改分仓
METHOD_TRY_WAREHOURSE = "try_warehourse"
# 调整分仓

# asset-api-protobuf 方法
METHOD_CELERY = "celery"  # 资管celery架构方法集
METHOD_GRAPH_QL = "graphql"  # 资管graphql架构方法集

# 转发进程方法
METHOD_QRY_ACCOUNTS = "qry_accounts"  # 查询账户
METHOD_ADD_ACCOUNT = "add_account"  # 新增账户
METHOD_DEL_ACCOUNT = "del_account"  # 删除账户
METHOD_BIND_ACCOUNT = "bind_account"  # 绑定账户
METHOD_UNBIND_ACCOUNT = "unbind_account"  # 解绑账户
METHOD_QRY_BIND = "qry_bindaccount"  # 查询绑定
METHOD_BATCH_MODIFY = "batch_modifyaccount"  # 批量修改账户
METHOD_ADD_BWLIST = "add_bwlist"  # 创建白名单
METHOD_UPDATE_BWLIST = "update_bwlist"  # 更新白名单
METHOD_DEL_BWLIST = "del_bwlist"  # 删除白名单
METHOD_QRY_BWLIST = "qry_bwlist"  # 查询白名单
METHOD_QRY_INSTITUTION = "qry_institution"  # 查询单个机构
METHOD_QRY_INSTITUTIONS = "qry_institutions"  # 查询多个机构
METHOD_UPDATE_INSTITUTION = "update_institution"  # 修改机构白名单
METHOD_CAN_LOGIN = "can_login"  # 判断是否能登录
METHOD_BATCH_DEL_ACCOUNTS = "batch_del_accounts"  # 批量删除账户

# 交易进程 方法
METHOD_TRADER_LOGIN = "login"  # 登录
METHOD_TRADER_LOGOUT = "logout"  # 登出
METHOD_TRADER_QUERY_INVESTOR = "query_investor"  # 查询投资者
METHOD_TRADER_CONFIRM_SETTLEMENT_INFO = "confirm_settlement_info"  # 确认结算单
METHOD_TRADER_QUERY_SETTLEMENT_INFO = "query_settlement_info"  # 查询投资者结算结果
METHOD_TRADER_QUERY_SETTLEMENT_INFO_CONFIRM = "query_settlement_confirm"  # 查询投资者结算确认
METHOD_TRADER_QUERY_ASSET = "query_asset"  # 查询资金
METHOD_TRADER_QUERY_ORDER = "query_order"  # 查询委托
METHOD_TRADER_QUERY_TRADE = "query_trade"  # 查询成交
METHOD_TRADER_QUERY_POSITION = "query_position"  # 查询持仓
METHOD_TRADER_QUERY_POSITION_DETAIL = "query_position_detail"  # 查询持仓明细
METHOD_TRADER_QUERY_COMMISSION_RATE = "query_commission_rate"  # 查询手续费率
METHOD_TRADER_QUERY_MARGIN_RATE = "query_margin_rate"  # 查询保证金费率
METHOD_TRADER_INSERT_ORDER = "insert_order"  # 委托
METHOD_TRADER_CANCEL_ORDER = "cancel_order"  # 撤单
METHOD_TRADER_BATCH_INSERT_ORDER = "batch_insert_order"  # 批量委托
METHOD_TRADER_BATCH_CANCEL_ORDER = "batch_cancel_order"  # 批量撤单
METHOD_TRADER_QUERY_INSTRUMENT = "query_instrument"  # 查询合约
METHOD_TRADER_USER_PASSWORD_UPDATE = "user_password_update"  # 修改密码
METHOD_TRADER_QUERY_MAX_ORDER_VOLUME = "query_max_order_volume"  # 查询最大报单数量请求
METHOD_TRADER_QUERY_TRADING_CODE = "query_trading_code"  # 查询交易编码
METHOD_TRADER_QUERY_NOTICE = "query_notice"  # 查询客户通知
METHOD_TRADER_QUERY_TRADING_NOTICE = "query_trading_notice"  # 查询交易通知
METHOD_TRADER_QUERY_CFMMC_ACCOUNT_TOKEN = "query_cfmmc_account_token"  # 查询监控中心用户令牌

# 条件单http网关方法
METHOD_CONDITION_GW_LOGIN = "login"  # 登录
METHOD_CONDITION_GW_CONDITION_ZL = "conditionzl"  # 请求统一方法
METHOD_CONDITION_GW_CONDITION = "condition"  # 请求统一方法

# 条件单进程方法
METHOD_CONDITION_ORDER_INSERT = "condition_order_insert"  # 新增条件单
METHOD_CONDITION_ORDER_MODIFY = "condition_order_modify"  # 修改条件单
METHOD_CONDITION_ORDER_PAUSE = "condition_order_pause"  # 暂停条件单
METHOD_CONDITION_ORDER_ACTIVATE = "condition_order_activate"  # 激活条件单
METHOD_CONDITION_ORDER_DELETE = "condition_order_delete"  # 删除条件单
METHOD_CONDITION_ORDER_QUERY = "condition_order_query"  # 查询单笔条件单
METHOD_CONDITION_ORDER_MULTIQUERY = "condition_order_multiquery"  # 查询多笔条件单
METHOD_CONDITION_ORDER_CANCEL = "condition_order_cancel"  # 取消条件单
METHOD_CONDITION_SETTLE = "condition_settle"  # 处理条件单日终日初

# 嵌套条件单进程方法
METHOD_NEST_CONDITION_INSERT = "nest_condition_insert"  # 新增嵌套条件单
METHOD_NEST_CONDITION_QUERY = "nest_condition_query"  # 条件单查询（附带嵌套条件单信息）
METHOD_NEST_CONDITION_MODIFY = "nest_condition_modify"  # 修改嵌套条件单

# 订单管理 方法
METHOD_ORDER_QUERY_ASSET = "query_asset"  # 查询资产
METHOD_ORDER_QUERY_ORDER = "query_order"  # 查询委托
METHOD_ORDER_QUERY_TRADE = "query_trade"  # 查询成交
METHOD_ORDER_QUERY_POSITION = "query_position"  # 查询持仓
METHOD_ORDER_QUERY_POSITION_DETAIL = "query_position_detail"  # 查询持仓明细
METHOD_ORDER_QUERY_COMMISSION_RATE = "query_commission_rate"  # 查询手续费率
METHOD_ORDER_QUERY_MARGIN_RATE = "query_margin_rate"  # 查询保证金费率
METHOD_ORDER_QUERY__RATE = "query_rate"  # 查询费率
METHOD_ORDER_INSERT_ORDER = "insert_order"  # 委托
METHOD_ORDER_CANCEL_ORDER = "cancel_order"  # 撤单
METHOD_ORDER_BATCH_INSERT_ORDER = "batch_insert_order"  # 批量委托
METHOD_ORDER_BATCH_CANCEL_ORDER = "batch_cancel_order"  # 批量撤单
METHOD_ORDER_INSERT_ORDER_T = "insert_order_t"  # 委托（兼容指令模块，预计2020年10月份删除）
METHOD_ORDER_CANCEL_ORDER_T = "cancel_order_t"  # 撤单（兼容指令模块，预计2020年10月份删除）
METHOD_ORDER_INSERT_ORDER_JGB = "insert_order_jgb"  # 委托（兼容机构版普通下单）

# 行情进程 方法
METHOD_QUOTER_QUERY_LAST_QUOTE = "query_last_quote"  # 查询最新快照
METHOD_QUOTER_SUB_LAST_QUOTE = "subscribe_last_quote"  # 订阅最新行情
METHOD_QUOTER_UNSUB_LAST_QUOTE = "unsubscribe_last_quote"  # 取消订阅最新行情
METHOD_QUOTER_SUB_TICK_QUOTE = "subscribe_tick_quote"  # 订阅逐笔行情
METHOD_QUOTER_UNSUB_TICK_QUOTE = "unsubscribe_tick_quote"  # 取消订阅逐笔行情
METHOD_QUOTER_SUB_TRADE = "subscribe_trade"  # 订阅成交
METHOD_QUOTER_UNSUB_TRADE = "unsubscribe_trade"  # 取消订阅成交
METHOD_QUOTER_SUB_ORDER = "subscribe_order"  # 订阅委托
METHOD_QUOTER_UNSUB_ORDER = "unsubscribe_order"  # 取消订阅委托
METHOD_QUOTER_SUB_ORDER_QUEUE = "subscribe_order_queue"  # 订阅委托队列
METHOD_QUOTER_UNSUB_ORDER_QUEUE = "unsubscribe_order_queue"  # 取消订阅委托队列
METHOD_QUOTER_QUERY_MAX_ACTIVE_INSTRUMENT = "query_max_active_instrument"  # 查询主力合约
METHOD_QUOTER_QUERY_INSTRUMENT = "query_instrument"  # 查询合约
METHOD_QUOTER_QUERY_SECURITY = "query_security"  # 查询证券

# 行情数据 方法
METHOD_MD_QUERY_LAST_QUOTE = "query_last_quote"  # 查询最新行情
METHOD_MD_QUERY_MAX_ACTIVE_INSTRUMENT = "query_max_active_instrument"  # 查询主力合约
METHOD_MD_QUERY_INSTRUMENT = "query_instrument"  # 查询合约
METHOD_MD_QUERY_SECURITY = "query_security"  # 查询证券
METHOD_MD_QUERY_BAR_DATA = "query_bar_data"  # 查询k线数据
METHOD_MD_QUERY_SHARES_DATA = "query_shares_data"  # 查询新股数据
METHOD_MD_QUERY_BILLBOARD_DATA = "query_billboard_data"  # 查询龙虎榜数据
METHOD_MD_QUERY_BATCH_BAR_DATA = "query_batch_bar_data"  # 批量查询k线数据
METHOD_MD_QUERY_TRADE_DAY = "query_trading_day"  # 查询交易日
METHOD_MD_QUERY_TICK_DETAIL = "query_tick_detail"  # 查询成交明细

# 账户进程 方法
METHOD_ACCOUNT_USER_AUTH = "user_auth"  # 客户端验证
METHOD_ACCOUNT_LOGIN = "login"  # 资金账户登录
METHOD_ACCOUNT_LOGOUT = "logout"  # 资金账户登出
METHOD_ACCOUNT_QUERY_ACCOUNT = "query_account"  # 查询资金账户数据
METHOD_ACCOUNT_QUERY_ACCOUNT_LIST = "query_account_list"  # 查询资金账户列表
METHOD_ACCOUNT_QUERY_LOGINED_ACCOUNTS = "query_logined_accounts"  # 查询已登录资金账户列表
METHOD_ACCOUNT_DELETE = "delete"  # 删除资金账户

# 信号进程 方法
METHOD_SIGNAL_SUBSCRIBE = "subscribe"  # 信号订阅
METHOD_SIGNAL_UNSUBSCRIBE = "unsubscribe"  # 信号取消订阅
METHOD_SIGNAL_HEALTH_CHECK = "health_check"  # 保活信息

# 策略管理进程 方法
METHOD_STRATEGY_START_PROCESS = "start_process"  # 启动策略进程
METHOD_STRATEGY_STOP_PROCESS = "stopc_process"  # 停止策略进程
METHOD_STRATEGY_QUERY_ALIVE_PROCESS_LIST = "query_alive_process_list"  # 查询正在运行的策略列表
METHOD_STRATEGY_HEALTH_CHECK = "health_check"  # 进程保活

# transmid
METHOD_TRANSMID_TRADER_LOGIN = "trader_login"  # 登录
METHOD_TRANSMID_TRADER_LOGOUT = "trader_logout"  # 登出
METHOD_TRANSMID_TRADER_QUERY_ASSET = "trader_query_asset"  # 查询资产
METHOD_TRANSMID_TRADER_QUERY_ORDER = "trader_query_orders"  # 查询委托
METHOD_TRANSMID_TRADER_QUERY_TRADE = "trader_query_traders"  # 查询成交
METHOD_TRANSMID_TRADER_QUERY_POSITION = "trader_query_position"  # 查询持仓
METHOD_TRANSMID_TRADER_INSERT_ORDER = "trader_insert_order"  # 委托
METHOD_TRANSMID_TRADER_CANCEL_ORDER = "trader_cancel_order"  # 撤单

# 银期转账
METHOD_TRADER_TRADING_ACCOUNT_PASSWORD_UPDATE = "trading_account_password_update"  # 资金账户口令更新请求
METHOD_TRADER_QUERY_CONTRACT_BANK = "query_contract_bank"  # 查签约银行
METHOD_TRADER_QUERY_ACCOUNT_REGISTER = "query_account_register"  # 查询银期签约关系
METHOD_TRADER_QUERY_TRANSFER_SERIAL = "query_transfer_serial"  # 查询转帐流水
METHOD_TRADER_QUERY_BANK_ACCOUNT_MONEY = "query_bank_account_money"  # 查询银行余额
METHOD_TRADER_FROM_BANK_TO_FUTURE = "from_bank_to_future"  # 银行资金转期货
METHOD_TRADER_FROM_FUTURE_TO_BANK = "from_future_to_bank"  # 期货资金转银行

# 风控服务
METHOD_RISK_VIARISK = "viarisk"  # 风控校验

# 客户端版本管理方法
METHOD_VERSION_MANAGER_INSERT = "insert"  # 新增版本
METHOD_VERSION_MANAGER_MODIFY = "modify"  # 修改版本
METHOD_VERSION_MANAGER_GO_ONLINE = "go_online"  # 上线版本
METHOD_VERSION_MANAGER_SET_BLACKLIST = "set_blacklist"  # 设置黑名单
METHOD_VERSION_MANAGER_QUERY = "query"  # 查询版本信息
METHOD_VERSION_MANAGER_DELETE = "delete"  # 删除版本
METHOD_VERSION_MANAGER_QUERY_ONLINE = "query_online"  # 查询线上版本
METHOD_VERSION_MANAGER_QUERY_SERVICE = "query_service"  # 查询服务器列表
METHOD_VERSION_MANAGER_INSERT_SERVICE = "insert_service"  # 新增服务器
METHOD_VERSION_MANAGER_DELETE_SERVICE = "delete_service"  # 删除服务器
METHOD_VERSION_MANAGER_INSERT_PRODUCT = "insert_product"  # 新增客户端类型
METHOD_VERSION_MANAGER_DELETE_PRODUCT = "delete_product"  # 删除客户端类型
METHOD_VERSION_MANAGER_QUERY_PRODUCT = "query_product"  # 查询客户端类型
METHOD_VERSION_MANAGER_QUERY_USER_VERSION = "query_user_version"  # 查询指定用户客户端版本绑定
METHOD_VERSION_MANAGER_SET_USER_VERSION = "set_user_version"  # 设置指定用户客户端版本绑定
METHOD_VERSION_MANAGER_MODIFY_USER_VERSION = "modify_user_version"  # 修改指定用户客户端版本绑定
METHOD_VERSION_MANAGER_DELETE_USER_VERSION = "delete_user_version"  # 删除指定用户客户端版本绑定

# 配置管理模块
METHOD_QUERY_CONFIG = "query_config"
# 监控管理中心
METHOD_QUERY_TARGETVALUE = "query_target_value"
# 监控客户端
CLIENT_MONITOR_RELAY_NODE = "monitor_relay_node"
METHOD_MONITOR_QUERY_METRICS = "query"  # 转发模块支持查询接口
