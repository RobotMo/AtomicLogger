import AtomicLogger
import logging
import threading
import random
from time import sleep
from concurrent.futures import ThreadPoolExecutor

# 最简单的方式，但只能配置 root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = AtomicLogger.ALogger.setup_normal_logger(
    __name__,
    logging.DEBUG,
    None,
    "[%(asctime)s][%(name)s][%(filename)s line %(lineno)d][%(levelname)s] : %(message)s"
)

def worker(i):
    global logger
    sleep(random.randint(0,4))
    logger.error(f"worker {i} normal error msg")
    logger.info(f"worker {i} normal error msg")
    with AtomicLogger.ALogger(logger, block_name=f"Thread {threading.get_ident()}, worker {i} Res Block") as alogger:
        for _ in range(5):
            alogger.atom_error(f"worker {i} error working process, result is {random.randint(0, 1)}")
            sleep(0.5)

with ThreadPoolExecutor(max_workers=64) as excutor:
    items = list(range(100))
    excutor.map(worker, items)

print("**" * 30 + "END" + "**" * 30)
