import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy

BASE_URL = 'https://www.freeproxylists.net/zh/?page={page_index}'
MAX_PAGE_INDEX = 10


class FreeproxyFetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for index in range(1, MAX_PAGE_INDEX):
            url = BASE_URL.format(page_index=index)
            html_text = self.get(url)
            if html_text:
                html = etree.HTML(html_text)
                if len(html.xpath('//tbody/tr[@class="Odd" or @class="Even" and not(@style)]')) > 0:
                    self.urls.append(url)
                else:
                    break

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr in html.xpath('//tbody/tr[@class="Odd" or @class="Even" and not(@style)]'):
            ip = tr.xpath('/td/a/text()')[0]
            port = tr.xpath('./td/text()')[1]
            protocol = tr.xpath('./td/text()')[2].lower()
            yield Proxy(ip=ip, port=port, protocol=protocol)
