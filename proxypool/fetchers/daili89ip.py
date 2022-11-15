import typing

from lxml import etree

from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


BASE_URL = 'https://www.89ip.cn/index_{page_index}.html'
MAX_PAGE_INDEX = 50


class DaiLi89Fetcher(BaseFetcher):
    def __init__(self):
        self.urls = []
        for index in range(1, MAX_PAGE_INDEX):
            url = BASE_URL.format(page_index=index)
            html_text = self.get(url)
            if html_text:
                html = etree.HTML(html_text)
                if len(html.xpath('//tbody/tr')) > 0:
                    self.urls.append(url)
                else:
                    break

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr_index, tr in enumerate(html.xpath('//tbody/tr')):
            ip = tr.xpath('./td/text()')[0].strip()
            port = tr.xpath('./td/text()')[1].strip()
            yield Proxy(ip=ip, port=port)
