import time
import multiprocessing
import platform
from gevent.pywsgi import WSGIServer
from proxypool.fetchers import classes as all_fetcher_class
from proxypool.checker import Checker
from proxypool.api import app
from proxypool.setting import FETCH_CYCLE, CHECK_CYCLE, ENABLE_FETCHER, \
    ENABLE_CHECKER, ENABLE_SERVER, API_HOST, API_PORT, \
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from proxypool.utils.log import logger
from proxypool.storages.redisClient import RedisClient


if platform.system().lower() == 'windows':
    multiprocessing.freeze_support()


fetcher_process, checker_process, server_process = None, None, None
db = RedisClient(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)


class Scheduler:
    """
    scheduler
    """
    @staticmethod
    def run_fetcher(cycle=FETCH_CYCLE):
        """
        run fetcher
        """
        loop = 1
        while True:
            logger.info(f'fetcher loop {loop} start')
            for fetcher_class in all_fetcher_class:
                try:
                    fetcher = fetcher_class()
                    for proxy in fetcher.fetch():
                        db.add(proxy)
                except Exception as e:
                    logger.error(f' an error occurred in the {fetcher_class.__name__} fetcher, error: {e}')
            loop += 1
            time.sleep(cycle)

    @staticmethod
    def run_checker(cycle=CHECK_CYCLE):
        """
        run checker
        """
        loop = 1
        checker = Checker()
        while True:
            logger.info(f'checker loop {loop} start')
            try:
                checker.run()
            except Exception as e:
                logger.error(f' an error occurred in the checker, error: {e}')
            loop += 1
            time.sleep(cycle)

    @staticmethod
    def run_server():
        """
        run server for api
        """
        http_server = WSGIServer((API_HOST, API_PORT), app)
        http_server.serve_forever()

    def run(self):
        global fetcher_process, checker_process, server_process
        try:
            logger.info('starting proxypool')
            if ENABLE_FETCHER:
                fetcher_process = multiprocessing.Process(target=self.run_fetcher)
                logger.info(f'starting fetcher, pid {fetcher_process.pid}')
                fetcher_process.start()

            if ENABLE_CHECKER:
                checker_process = multiprocessing.Process(target=self.run_checker)
                logger.info(f'starting checker, pid {checker_process.pid}')
                checker_process.start()

            if ENABLE_SERVER:
                server_process = multiprocessing.Process(target=self.run_server)
                logger.info(f'starting server, pid {server_process.pid}')
                server_process.start()

            fetcher_process and fetcher_process.join()
            checker_process and checker_process.join()
            server_process and server_process.join()
        except KeyboardInterrupt:
            logger.info('received keyboard interrupt signal')
            fetcher_process and fetcher_process.terminate()
            checker_process and checker_process.terminate()
            server_process and server_process.terminate()
        finally:
            logger.info('proxy terminated')


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
