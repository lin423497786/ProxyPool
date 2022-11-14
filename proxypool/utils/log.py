import os
import logging
import platform
from logging.handlers import TimedRotatingFileHandler
from proxypool.setting import LOG_LEVEL


class LogHandler(logging.Logger):
    """
    LogHandler
    """

    def __init__(self, name, level=logging.DEBUG, stream=True, file=True, log_dir_path=''):
        self.name = name
        self.level = level
        self.log_dir_path = log_dir_path
        logging.Logger.__init__(self, self.name, level=level)
        if stream:
            self.__setStreamHandler__()
        if file:
            if platform.system() != "Windows":
                self.__setFileHandler__()

    def __setFileHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        log_file_path = os.path.join(self.log_dir_path, '{name}.log'.format(name=self.name))
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        file_handler = TimedRotatingFileHandler(filename=log_file_path, when='D', interval=1, backupCount=15)
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s [%(name)s] [%(filename)s:%(lineno)d] [%(levelname)s]: %(message)s')

        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def __setStreamHandler__(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(name)s] [%(filename)s:%(lineno)d] [%(levelname)s]: %(message)s')
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self.level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)


logger = LogHandler('proxy', level=LOG_LEVEL, file=False)
