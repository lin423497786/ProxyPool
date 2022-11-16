import typing
import re
from urllib.parse import urljoin
from lxml import etree
from proxypool.fetchers.base import BaseFetcher
from proxypool.schema import Proxy


class ProxylistFetcher(BaseFetcher):
    urls = [
        'https://proxylist.live/nodes/free_2.php',
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://www.proxyscan.io/download?type=http',
        'https://api.openproxylist.xyz/http.txt',
        'http://alexa.lr2b.com/proxylist.txt',
        'http://rootjazz.com/proxies/proxies.txt',
        'https://www.freeproxychecker.com/result/http_proxies.txt',
        'https://multiproxy.org/txt_all/proxy.txt',
        'https://proxy-spider.com/api/proxies.example.txt',
        'http://spys.me/proxy.txt'
    ]

    def parse(self, html: typing.Optional[str]):
        pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)', re.I)
        for line in html.split('\n'):
            if line.strip() and not line.startswith('#'):
                result = pattern.search(line)
                if result:
                    ip = result.group(1)
                    port = int(result.group(2))
                    yield Proxy(ip=ip, port=port)
