import typing
from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


BASE_URL = 'http://www.66ip.cn/{index}.html'
MAX_PAGE_INDEX = 10


class DaiLi66Fetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for index in range(1, MAX_PAGE_INDEX):
            url = BASE_URL.format(index=index)
            html_text = self.get(url)
            if html_text:
                html = etree.HTML(html_text)
                if len(html.xpath('//table[@width="100%"]//tr')) > 1:
                    self.urls.append(url)
                else:
                    break

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr_index, tr in enumerate(html.xpath('//table[@width="100%"]//tr')):
            if tr_index == 0:
                continue
            else:
                ip = tr.xpath('./td/text()')[0]
                port = tr.xpath('./td/text()')[1]
                yield Proxy(ip=ip, port=port)


if __name__ == '__main__':
    from proxypool.storages.redisClient import RedisClient
    fetcher = DaiLi66Fetcher()
    client = RedisClient('192.168.19.128')
    for i in fetcher.fetch():
        client.add(i)
    print(client.count(state='all'))
