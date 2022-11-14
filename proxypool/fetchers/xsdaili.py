import typing
import re
from urllib.parse import urljoin
from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'https://www.xsdaili.cn/'


class XsdailiFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        html_text = self.get(BASE_URL)
        if html_text:
            html = etree.HTML(html_text)
            for url in html.xpath('//div[contains(@class, "table")]//div[@class="title"]/a/@href'):
                self.urls.append(urljoin(BASE_URL, url))

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)@(http|https)#', re.I)
        for line in html.xpath('//div[@class="cont"]/text()'):
            result = pattern.search(line)
            if result:
                ip = result.group(1)
                port = int(result.group(2))
                protocol = result.group(3).lower()
                yield Proxy(ip=ip, port=port, protocol=protocol)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = XsdailiFetcher()
    for i in fetcher.fetch():
        print(i)
    # client = RedisClient('192.168.19.128')
    # for i in fetcher.fetch():
    #     client.add(i)
    # print(client.count(state='all'))
