# ProxyPool

免费代理池，提供如下功能：

- 定时抓取免费代理网站的代理信息, 可扩展。
- 定时验证爬取下来的代理, 剔除不可用代理, 留下可用代理, 保证代理的可用性。
- 提供api, 方便提取可用的代理。


### 运行项目
- Python>=3.6

* 下载代码:

```bash
git clone https://github.com/lin423497786/ProxyPool.git
```

* 安装依赖:

```bash
pip install -r requirements.txt
```

* 更改配置:
```python
# proxypool/setting.py 为项目配置文件
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
...
```

* 启动项目:

```bash
cd proxypool; python3 scheduler.py
```


### 使用

* Api

启动服务后, 默认会在 http://127.0.0.1:9999 开启api接口服务:

| api | method | Description | params|
| ----| ---- | ---- | ----|
| / | GET | api介绍 | None |
| /random/ | GET | 随机获取多个代理| 可选参数: <br> `max_delay` 代理的最大延迟 <br>`min_success_count`最小的连续检测成功次数，<br>连续检测成功次数越多代表代理越稳定 <br>`number`代理个数,默认为1|
| /pop/ | GET | 随机获取并删除多个代理| 可选参数: <br> `max_delay` 代理的最大延迟 <br>`min_success_count`最小的连续检测成功次数，<br>连续检测成功次数越多代表代理越稳定 <br>`number`代理个数,默认为1|
| /all/ | GET | 获取所有代理 |None|
| /count/ | GET | 查看代理数量 |None|
| /clear/ | GET | 删除所有代理 |None|
| /delete/ | GET | 删除代理  |`proxy={PROTOCOL}://{IP}:{PORT}"`|

* 示例
```python
import requests

# 获取一个随机代理
url = 'http://127.0.0.1:9999/random/'
requests.get(url)

# 获取一个延时不超过1秒的代理
url = 'http://127.0.0.1:9999/random/?max_delay=1'
requests.get(url)

# 获取5个延时不超过1秒的代理
url = 'http://127.0.0.1:9999/random/?max_delay=1&number=5'
requests.get(url)

# 获取1个延时不超过1秒且连续检测成功4次的代理, 连续成功越多次代表代理越稳定
url = 'http://127.0.0.1:9999/random/?max_delay=1&number=1&min_success_count=4'
requests.get(url)



```

<br>
<br>