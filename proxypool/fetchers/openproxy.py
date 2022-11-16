import typing
import re

from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


class OpenproxyFetcher(BaseFetcher):
    urls = ['https://openproxy.space/list/http']

    def parse(self, html: typing.Optional[str]):
        pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)', re.I)
        for socket in pattern.findall(html):
            yield Proxy(ip=socket[0], port=int(socket[1]))
