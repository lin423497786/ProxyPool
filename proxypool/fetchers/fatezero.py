import typing
import json

from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


class FatezeroFetcher(BaseFetcher):
    urls = ['http://proxylist.fatezero.org/proxy.list']

    def parse(self, html: typing.Optional[str]):
        for proxy_info in html.split('\n'):
            if proxy_info:
                proxy_info_dict = json.loads(proxy_info)
                yield Proxy(
                    ip=proxy_info_dict['host'],
                    port=proxy_info_dict['port'],
                    protocol=proxy_info_dict['type']
                )
