import logging

# redis key
REDIS_KEY = 'proxies'

# redis 服务器的地址
REDIS_HOST = '192.168.174.128'

# redis服务器的监听端口
REDIS_PORT = 6379

# 连接redis服务器所使用的密码
REDIS_PASSWORD = ''

# api服务绑定的ip地址
API_HOST = '0.0.0.0'

# api服务监听的端口
API_PORT = 9999

# 只保存高匿名代理
ONLY_ANONYMOUS_PROXY = False

# 爬取超时时间
FETCH_TIMEOUT = 10

# 检测超时时间
CHECK_TIMEOUT = 10

# 检测的url
CHECK_URL = 'https://www.baidu.com/'

# 检测有效的状态
CHECK_VALID_STATUS = [200, 206, 302]

# 检测时的并发数
CHECK_BATCH_NUM = 200

# 代理的分数, 刚爬取下来的代理的分数将赋予PROXY_SCORE_INIT
# 检测失败分数减1,当分数低于PROXY_SCORE_MIN时候，该代理从数据库中删除
# 检测成功分数提高到PROXY_SCORE_MAX
PROXY_SCORE_MAX = 50
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 10

# 每隔多少秒调用代理爬取进程
FETCH_CYCLE = 12 * 3600

# 每隔多少秒调用代理检测进程
CHECK_CYCLE = 60

# 是否开启代理爬取进程
ENABLE_FETCHER = True

# 是否开启代理检测进程
ENABLE_CHECKER = True

# 是否开api服务进程
ENABLE_SERVER = True

# 是否开启对ip的归属地查询
ENABLE_LOCATION_QUERY = True

# 日志级别
LOG_LEVEL = logging.INFO
