import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


class SeofangfaFetcher(BaseFetcher):
    urls = ['https://proxy.seofangfa.com/']

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr in html.xpath('//tbody/tr'):
            ip = tr.xpath('./td/text()')[0]
            port = tr.xpath('./td/text()')[1]
            yield Proxy(ip=ip, port=port)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = SeofangfaFetcher()
    client = RedisClient('192.168.174.128')
    for i in fetcher.fetch():
        client.add(i)
    print(client.count(state='all'))
