from flask import Flask, request, g
from proxypool.storages.redisClient import RedisClient
from proxypool.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

app = Flask(__name__)

# 使通过jsonify返回的中文显示正常，否则显示为ASCII码
app.config["JSON_AS_ASCII"] = False

api_list = [
    {
        "url": "/random/",
        "params": "max_delay: mximum delay, min_success_count: minimum number of consecutive successes, "
                  "number: number of proxies",
        "desc": "get the specified number of proxies"
    },
    {"url": "/all/", "desc": "get all proxy from proxy pool"},
    {"url": "/count/",  "desc": "get all proxy count"},
    {"url": "/delete/", "params": "proxy: {PROTOCOL}://{IP}:{PORT}", "desc": "delete an proxy"},
    {
        "url": "/pop/",
        "params": "max_delay: mximum delay, min_success_count: minimum number of consecutive successes, "
                  "number: number of proxies",
        "desc": "get and delete the specified number of proxies"
    },
    {"url": "/clear/", "desc": "delete all proxy"
     },
]


def get_connect():
    if not hasattr(g, "redis"):
        g.redis = RedisClient(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )
    return g.redis


@app.route("/")
def index():
    return {"url": api_list}


@app.route("/random/")
def get_random_proxy():
    connect = get_connect()
    max_delay = request.args.get("max_delay", '')
    if max_delay.isdigit():
        max_delay = int(max_delay)
    else:
        max_delay = 9999

    min_success_count = request.args.get("min_success_count", '')
    if min_success_count.isdigit():
        min_success_count = int(min_success_count)
    else:
        min_success_count = 0

    number = request.args.get("number", '')
    if number.isdigit():
        number = int(number)
    else:
        number = 1
    all_proxy = connect.random(
        state='valid',
        max_delay=max_delay,
        min_success_count=min_success_count,
        number=number
    )
    if all_proxy:
        return {"code": 0, "msg": "success", "data": [proxy.to_dict() for proxy in all_proxy]}
    else:
        return {"code": 1, "msg": "no proxy in proxypool", "data": []}


@app.route("/all/")
def get_all_proxy():
    connect = get_connect()
    all_proxy = connect.get_all(state='valid')
    if all_proxy:
        return {"code": 0, "msg": "success", "data": [proxy.to_dict() for proxy in all_proxy]}
    else:
        return {"code": 1, "msg": "no proxy in proxypool", "data": []}


@app.route("/count/")
def get_count():
    connect = get_connect()
    count = connect.count(state='valid')
    return {"code": 0, "msg": "success", "data": count}


@app.route("/pop/")
def pop():
    connect = get_connect()
    max_delay = request.args.get("max_delay", '')
    if max_delay.isdigit():
        max_delay = int(max_delay)
    else:
        max_delay = 9999

    min_success_count = request.args.get("min_success_count", '')
    if min_success_count.isdigit():
        min_success_count = int(min_success_count)
    else:
        min_success_count = 0

    number = request.args.get("number", '')
    if number.isdigit():
        number = int(number)
    else:
        number = 1
    all_proxy = connect.pop(
        state='valid',
        max_delay=max_delay,
        min_success_count=min_success_count,
        number=number
    )
    if all_proxy:
        return {"code": 0, "msg": "success", "data": [proxy.to_dict() for proxy in all_proxy]}
    else:
        return {"code": 1, "msg": "no proxy in proxypool", "data": []}


@app.route("/delete/")
def delete_proxy():
    connect = get_connect()
    proxy = request.args.get("proxy", "")
    if proxy:
        delete_count = connect.delete(proxy)
        return {"code": 0, "msg": "success", "data": delete_count}
    else:
        return {"code": 1, "msg": "the parameter proxy is not specified, proxy like {PROTOCOL}://{IP}:{PORT}"}


@app.route("/clear/")
def refresh():
    connect = get_connect()
    connect.clear()
    return {"code": 0, "msg": "success"}


if __name__ == '__main__':
    from proxypool.setting import API_HOST, API_PORT
    app.run(host=API_HOST, port=API_PORT)
