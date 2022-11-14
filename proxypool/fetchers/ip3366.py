import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'http://www.ip3366.net/?stype=1&page={page_index}'


class Ip3366Fetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        url = BASE_URL.format(page_index=1)
        html_text = self.get(url)
        if html_text:
            html = etree.HTML(html_text)
            total_page = html.xpath('//strong/font/..//text()')[-1]
            total_page = int(total_page.replace('/', ''))
            for index in range(1, total_page + 1):
                self.urls.append(BASE_URL.format(page_index=index))

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr_index, tr in enumerate(html.xpath('//table/tbody/tr')):
            ip = tr.xpath('./td/text()')[0]
            port = tr.xpath('./td/text()')[1]
            protocol = tr.xpath('./td/text()')[3].lower()
            yield Proxy(ip=ip, port=port, protocol=protocol)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = Ip3366Fetcher()
    client = RedisClient('192.168.19.128')
    for i in fetcher.fetch():
        client.add(i)
    print(client.count(state='all'))
