import time
import asyncio
import aiohttp
from aiohttp import ClientProxyConnectionError, \
    ServerDisconnectedError, \
    ClientOSError, \
    ClientHttpProxyError,\
    ClientResponseError
from asyncio import TimeoutError
from proxypool.utils.log import logger
from proxypool.schema import Proxy
from proxypool.storages.redisClient import RedisClient
from proxypool.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, ONLY_ANONYMOUS_PROXY, \
    CHECK_TIMEOUT, CHECK_URL, CHECK_VALID_STATUS, CHECK_BATCH_NUM, ENABLE_LOCATION_QUERY

EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
    AssertionError,
    ClientResponseError
)


class Checker:
    """
    tester for testing proxies
    """

    def __init__(self):
        """
        init redis
        """
        self.db = RedisClient(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
        self.semaphore = asyncio.Semaphore(CHECK_BATCH_NUM)

    async def check(self, proxy: Proxy):
        """
        test single proxy
        :param proxy: Proxy object
        :return:
        """
        async with self.semaphore:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                try:
                    logger.debug(f'checking {proxy.to_string()}')
                    # 如果ONLY_ANONYMOUS_PROXY为True，需确保代理具有隐藏真实IP的效果即高匿名代理
                    if ONLY_ANONYMOUS_PROXY:
                        url = 'https://httpbin.org/ip'
                        async with session.get(url, timeout=CHECK_TIMEOUT) as response:
                            response_json = await response.json()
                            origin_ip = response_json['origin']
                        async with session.get(url, proxy=f'{proxy.to_string()}', timeout=CHECK_TIMEOUT) as response:
                            response_json = await response.json()
                            anonymous_ip = response_json['origin']
                        assert origin_ip != anonymous_ip
                        assert proxy.ip == anonymous_ip

                    # 检测代理是否有效
                    begin_time = time.time()
                    async with session.get(
                            CHECK_URL, proxy=f'{proxy.to_string()}', timeout=CHECK_TIMEOUT, allow_redirects=True
                    ) as response:
                        if response.status in CHECK_VALID_STATUS:
                            end_time = time.time()
                            proxy.delay = round(end_time - begin_time, 2)
                            # 获取ip所在的归属地
                            if ENABLE_LOCATION_QUERY and proxy.location == '':
                                try:
                                    url = f'https://ip.taobao.com/outGetIpInfo?ip={proxy.ip}&accessKey=alibaba-inc'
                                    async with session.get(url, timeout=CHECK_TIMEOUT) as location_response:
                                        location_info = await location_response.json()
                                        if location_info.get('code') == 0:
                                            country = location_info['data']['country']
                                            if location_info['data']['city'] != 'XX':
                                                city = location_info['data']['city']
                                            else:
                                                city = ''
                                            if location_info['data']['isp'] != 'XX':
                                                isp = location_info['data']['isp']
                                            else:
                                                isp = ''
                                            proxy.location = country + city + isp
                                except:
                                    proxy.location = ''

                            self.db.max(proxy)
                            logger.debug(f'proxy {proxy.to_string()} is valid, set max score')
                        else:
                            self.db.decrease(proxy)
                            logger.debug(f'proxy {proxy.to_string()} is invalid, decrease score')
                except EXCEPTIONS:
                    self.db.decrease(proxy)
                    logger.debug(f'proxy {proxy.to_string()} is invalid, decrease score')

    def run(self):
        """
        check main method
        :return:
        """
        loop = asyncio.get_event_loop()
        logger.info('stating checker')
        count = self.db.count(state='all')
        logger.info(f'{count} proxies to check')
        tasks = []
        for p in self.db.get_all(state='all'):
            if p.protocol.lower() == 'http':
                tasks.append(loop.create_task(self.check(p)))

        if tasks:
            # loop.run_until_complete(asyncio.wait(tasks))
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        logger.info('end checker')


if __name__ == '__main__':
    checker = Checker()
    checker.run()
