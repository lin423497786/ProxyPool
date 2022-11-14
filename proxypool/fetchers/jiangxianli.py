import typing
import re
from urllib.parse import urljoin
from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'https://ip.jiangxianli.com/?page={page_index}'
MAX_PAGE_INDEX = 10


class JiangxianliFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for index in range(1, MAX_PAGE_INDEX):
            url = BASE_URL.format(page_index=index)
            html_text = self.get(url)
            if html_text:
                html = etree.HTML(html_text)
                if len(html.xpath('//tbody/tr')) > 1:
                    self.urls.append(url)
                else:
                    break

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr in html.xpath('//tbody/tr'):
            if len(tr.xpath('./td/text()')) >= 3:
                ip = tr.xpath('./td/text()')[0]
                port = tr.xpath('./td/text()')[1]
                protocol = tr.xpath('./td/text()')[3].lower()
                yield Proxy(ip=ip, port=port, protocol=protocol)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = JiangxianliFetcher()
    # for i in fetcher.fetch():
    #     print(i)
    client = RedisClient('192.168.174.128')
    for i in fetcher.fetch():
        client.add(i)
    # print(client.count(state='all'))
