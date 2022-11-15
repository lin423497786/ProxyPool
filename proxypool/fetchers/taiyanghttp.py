import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'http://www.taiyanghttp.com/free/page{page_index}/'
MAX_PAGE_INDEX = 10


class TaiyanghttpFetcher(BaseFetcher):
    urls = [BASE_URL.format(page_index=i) for i in range(1, MAX_PAGE_INDEX+1)]

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr in html.xpath('//div[@id="ip_list"]//div[contains(@class, "tr")]'):
            ip = tr.xpath('./div[contains(@class, "td")]/text()')[0]
            port = tr.xpath('./div[contains(@class, "td")]/text()')[1]
            protocol = tr.xpath('./div[contains(@class, "td")]/text()')[5].lower()
            yield Proxy(ip=ip, port=port, protocol=protocol)
