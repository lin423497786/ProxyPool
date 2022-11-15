import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

ALL_BASE_URL = ['https://www.kuaidaili.com/free/inha/{page_index}', 'https://www.kuaidaili.com/free/intr/{page_index}']
MAX_PAGE_INDEX = 10


class KuaidailiFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for base_url in ALL_BASE_URL:
            for index in range(1, MAX_PAGE_INDEX+1):
                url = base_url.format(page_index=index)
                self.urls.append(url)

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr_index, tr in enumerate(html.xpath('//tbody/tr')):
            ip = tr.xpath('./td/text()')[0]
            port = tr.xpath('./td/text()')[1]
            protocol = tr.xpath('./td/text()')[3].lower()
            yield Proxy(ip=ip, port=port, protocol=protocol)
