import typing

import requests
import faker
from proxypool.utils.log import logger
from proxypool.setting import FETCH_TIMEOUT

requests.packages.urllib3.disable_warnings()


class BaseFetcher:
    urls = []
    headers = {
        'User-Agent': faker.Faker().user_agent(),
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }

    def get(
            self,
            url: typing.Optional[str],
            retry_times: typing.Optional[int] = 3,
            timeout: typing.Optional[int] = FETCH_TIMEOUT,
            **kwargs
    ) -> typing.Optional[str]:
        """

        :param url:
        :param retry_times: 尝试次数
        :param timeout: 访问页面超时时间
        :param kwargs:
        :return: 返回页面的文本
        """
        # 设置访问headers
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers

        #
        if url.startswith('https') or url.startswith('HTTPS'):
            kwargs['verify'] = False

        for _ in range(retry_times):
            try:
                response = requests.get(url, timeout=timeout, **kwargs)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        else:
            logger.error(
                f'failed to crawl proxy information from url {url},'
                f' please check if target url is valid or network issue'
            )
            return

    def fetch(self):
        for url in self.urls:
            logger.debug(f'fetching {url}')
            html_text = self.get(url)
            if not html_text:
                continue
            count = 0
            for proxy in self.parse(html_text):
                count += 1
                logger.debug(f'fetched proxy "{proxy.to_string()}" from "{url}"')
                yield proxy
            logger.info(f'{url} website crawling completed, number of proxies: {count}')


    def parse(self, html: typing.Optional[str]):
        pass
