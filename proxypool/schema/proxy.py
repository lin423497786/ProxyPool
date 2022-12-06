import typing
import json

from proxypool.setting import PROXY_SCORE_INIT


class Proxy:
    def __init__(
            self,
            ip: typing.Optional[str],
            port: typing.Optional[int],
            protocol: typing.Optional[str] = 'http',
            location: typing.Optional[str] = '',
            source: typing.Optional[str] = 'unknown',
            score: typing.Optional[int] = PROXY_SCORE_INIT,
            delay: typing.Optional[float] = 9999,
            success_count: typing.Optional[int] = 0
    ):
        self._ip = ip
        self._port = port
        if protocol.lower() == 'http' or protocol.lower() == 'https':
            self._protocol = protocol.lower()
        else:
            self._protocol = 'http'

        self._location = location
        self._score = score
        self._delay = delay

        # 最近连续检测连接成功的次数
        self._success_count = success_count

        self._source = source

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def protocol(self):
        return self._protocol

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def score(self):
        return self._score

    @property
    def delay(self):
        return self._delay

    @property
    def success_count(self):
        return self._success_count

    @score.setter
    def score(self, value):
        self._score = value

    @delay.setter
    def delay(self, value):
        self._delay = value

    @success_count.setter
    def success_count(self, value):
        self._success_count = value

    def __str__(self):
        return '{protocol}://{ip}:{port}'.format(
            protocol=self.protocol,
            ip=self.ip,
            port=self.port
        )

    def to_string(self):
        return self.__str__()

    def to_dict(self):
        return {
            'ip': self.ip,
            'port': self.port,
            'protocol': self.protocol,
            'location': self.location,
            'source': self.source,
            'delay': self.delay,
            'score': self.score,
            'success_count': self.success_count
        }

    def to_json(self):
        return json.dumps(self.to_dict())


if __name__ == '__main__':
    p = Proxy('1.1.1.1', port=80, protocol='http')
    print(p, p.to_string(), p.ip)
    print(p.to_json())
