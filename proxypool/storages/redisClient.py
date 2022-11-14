import typing
import json
import redis
from random import sample
from proxypool.schema.proxy import Proxy
from proxypool.setting import REDIS_KEY, PROXY_SCORE_MIN, PROXY_SCORE_MAX
from proxypool.utils.log import logger


class RedisClient:
    def __init__(
            self,
            host: typing.Optional[str],
            port: typing.Optional[int] = 6379,
            password: typing.Optional[str] = None,
            **kwargs
    ):
        self.db = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            **kwargs
        )

    def add(self, proxy: Proxy):
        """将代理信息添加到hash表中

        :param proxy: proxypool.schema.proxy.Proxy
        :return:
        """
        if not self.db.hexists(REDIS_KEY, proxy.to_string()):
            return self.db.hset(REDIS_KEY, proxy.to_string(), proxy.to_json())

    def delete(self, proxy_string: typing.Optional[str]):
        """删除指定代理

        :param proxy_string: "PROTOCOL://IP:PORT"
        :return:
        """
        return self.db.hdel(REDIS_KEY, proxy_string)

    def get(self, proxy_string: typing.Optional[str]):
        """ 获取一个代理的信息

        :param proxy_string: "PROTOCOL://IP:PORT"
        :return:
        """
        proxy_info = self.db.hget(REDIS_KEY, proxy_string)
        return Proxy(**json.loads(proxy_info)) if proxy_info else None

    def get_all(
            self,
            state: typing.Optional[str] = 'valid'
    ) -> [Proxy]:
        """获取所有代理的信息

        :param state: ['valid', 'invalid', 'all']
        :return:
        """
        all_proxy = self.db.hvals(REDIS_KEY)
        if state == 'valid':
            all_proxy = list(filter(lambda x: json.loads(x).get('score') == PROXY_SCORE_MAX, all_proxy))
        elif state == 'invalid':
            all_proxy = list(filter(lambda x: json.loads(x).get('score') != PROXY_SCORE_MAX, all_proxy))

        return [Proxy(**json.loads(p)) for p in all_proxy]

    def count(
            self,
            state: typing.Optional[str] = 'valid',

    ) -> int:
        """统计代理数量

        :param state: ['valid', 'invalid', 'all']
        :return:
        """
        return len(self.get_all(state=state))

    def random(
            self,
            state: typing.Optional[str] = 'valid',
            max_delay: typing.Optional[float] = 9999,
            min_success_count: typing.Optional[int] = 1,
            number: typing.Optional[int] = 1
    ) -> [Proxy]:
        """获取指定数量的随机代理

        :param state: ['valid', 'invalid', 'all']
        :param max_delay: 代理的最大延时
        :param min_success_count: 代理最近检测成功的最小次数
        :param number: 代理数量
        :return:
        """
        all_valid_proxy = self.get_all(state=state)
        all_valid_proxy = list(filter(lambda x: x.delay <= max_delay, all_valid_proxy))
        all_valid_proxy = list(filter(lambda x: x.success_count >= min_success_count, all_valid_proxy))
        proxy_number = min(len(all_valid_proxy), number)
        return sample(all_valid_proxy, proxy_number) if all_valid_proxy else None

    def pop(
            self,
            state: typing.Optional[str] = 'valid',
            max_delay: typing.Optional[float] = 9999,
            min_success_count: typing.Optional[int] = 1,
            number: typing.Optional[int] = 1
    ) -> [Proxy]:
        """弹出一个有效的随机代理

        :param state: ['valid', 'invalid', 'all']
        :param max_delay: 代理的最大延时
        :param min_success_count: 代理最近检测成功的最小次数
        :param number: 代理数量
        :return:
        """
        all_proxy = self.random(state=state, max_delay=max_delay, min_success_count=min_success_count, number=number)
        if all_proxy:
            for proxy in all_proxy:
                self.delete(proxy.to_string())
        return all_proxy

    def exists(self, proxy_string: typing.Optional[str]):
        """判断代理是否存在

        :param proxy_string: "PROTOCOL://IP:PORT"
        :return:
        """
        return self.db.hexists(REDIS_KEY, proxy_string)

    def max(self, proxy: typing.Optional[Proxy]):
        proxy.score = PROXY_SCORE_MAX
        proxy.success_count = proxy.success_count + 1
        return self.db.hset(REDIS_KEY, proxy.to_string(), proxy.to_json())

    def decrease(self, proxy: typing.Optional[Proxy]):
        proxy.score = proxy.score - 1
        proxy.success_count = 0
        if proxy.score <= PROXY_SCORE_MIN:
            logger.debug(f'{proxy.to_string()} current score {proxy.score}, remove')
            self.db.hdel(REDIS_KEY, proxy.to_string())
        else:
            self.db.hset(REDIS_KEY, proxy.to_string(), proxy.to_json())
        return proxy

    def clear(self):
        self.db.delete(REDIS_KEY)

    def __del__(self):
        self.db.close()


if __name__ == '__main__':
    client = RedisClient('192.168.19.128')
    # add
    print('{mark}add{mark}'.format(mark='*'*30))
    p1 = Proxy(ip='8.8.8.8', port=8080)
    print(client.add(p1))
    p2 = Proxy(ip='8.8.8.8', port=8888, protocol='https')
    print(client.add(p2))

    # delete
    print('{mark}delete{mark}'.format(mark='*' * 30))
    print(client.delete('http://8.8.8.8:8086'))

    # random
    print('{mark}random{mark}'.format(mark='*' * 30))
    random_proxy = client.random()
    print(random_proxy.to_json())

    # exists
    print('{mark}exists{mark}'.format(mark='*' * 30))
    print(client.exists('http://8.8.8.8:8080'))
    print(client.exists('https://8.8.8.8:8080'))

    # count
    print('{mark}count{mark}'.format(mark='*' * 30))
    print(client.count())
    print(client.count())
    print(client.count())

    # get_all
    print('{mark}get_all{mark}'.format(mark='*' * 30))
    print(client.get_all())
    print(client.get_all())
    print(client.get_all())

    # pop
    print('{mark}pop{mark}'.format(mark='*' * 30))
    random_proxy = client.pop()
    print(random_proxy.to_json())
    print(client.exists(random_proxy.to_string()))

    # clear
    print('{mark}clear{mark}'.format(mark='*' * 30))
    print(client.clear())
    print(client.count())

    # max
    print('{mark}max{mark}'.format(mark='*' * 30))
    p = Proxy(ip='2.2.2.2', port=80)
    print(client.max(p))
    p1 = client.get(p.to_string())
    print(p1.to_dict())

    # decrease
    print('{mark}decrease{mark}'.format(mark='*' * 30))
    p = Proxy(ip='2.2.2.2', port=80)
    for i in range(10):
        p = client.decrease(p)
        print(p.to_dict())
