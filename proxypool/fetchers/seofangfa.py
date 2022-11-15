import typing

from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


class SeofangfaFetcher(BaseFetcher):
    urls = ['https://proxy.seofangfa.com/']

    def parse(self, html: typing.Optional[str]):
        html = etree.HTML(html)
        for tr in html.xpath('//tbody/tr'):
            ip = tr.xpath('./td/text()')[0]
            port = tr.xpath('./td/text()')[1]
            yield Proxy(ip=ip, port=port)
