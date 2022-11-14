import typing
import re
from urllib.parse import urljoin
from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'https://www.zdaye.com/'


class ZdayeFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        html_text = self.get('https://www.zdaye.com/dayProxy/1.html')
        if html_text:
            html = etree.HTML(html_text)
            for index, url in enumerate(html.xpath('//div[@class="thread_item"]//h3/a/@href')):
                if index <= 4:
                    self.urls.append(urljoin(BASE_URL, url))

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        ip_pattern = re.compile(r'(\d+\.){3}\d+')
        port_pattern = re.compile(r'\d+')
        for tr in html.xpath('//tbody/tr'):
            ip = ip_pattern.search(tr.xpath('./td/text()')[0]).group()
            port = int(port_pattern.search(tr.xpath('./td/text()')[1]).group())
            yield Proxy(ip=ip, port=port)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = ZdayeFetcher()
    # for i in fetcher.fetch():
    #     print(i)
    client = RedisClient('192.168.174.128')
    for i in fetcher.fetch():
        client.add(i)
    # print(client.count(state='all'))
