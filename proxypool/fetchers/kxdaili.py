import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

ALL_BASE_URL = ['http://www.kxdaili.com/dailiip/1/{page_index}.html',
                'http://www.kxdaili.com/dailiip/2/{page_index}.html']
MAX_PAGE_INDEX = 10


class KxdailiFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for base_url in ALL_BASE_URL:
            for index in range(1, MAX_PAGE_INDEX+1):
                url = base_url.format(page_index=index)
                html_text = self.get(url)
                if html_text:
                    html = etree.HTML(html_text)
                    if len(html.xpath('//table[@class="active"]/tbody/tr')) > 0:
                        self.urls.append(url)

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr_index, tr in enumerate(html.xpath('//table[@class="active"]/tbody/tr')):
            ip = tr.xpath('./td/text()')[0]
            port = tr.xpath('./td/text()')[1]
            protocol = tr.xpath('./td/text()')[3].lower()
            yield Proxy(ip=ip, port=port, protocol=protocol)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = KxdailiFetcher()
    client = RedisClient('192.168.19.128')
    for i in fetcher.fetch():
        client.add(i)
    print(client.count(state='all'))
