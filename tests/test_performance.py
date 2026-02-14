from functools import partial
import pytest
import time
import fire
from AtomicLogger import *
from concurrent.futures import ThreadPoolExecutor

logger = ALogger.setup_normal_logger(
    __name__,
    logging.DEBUG,
    "test.log",
    "[%(asctime)s][%(name)s][%(filename)s line %(lineno)d][%(levelname)s] : %(message)s"
)

def worker(i, a_times=5):
    # logger.info(f"start worker {i}")
    # bname = f"Block For worker-{i}"
    # logger.info(bname)
    with ALogger(logger, f"Block For worker-{i}") as alog:
        for _ in range(a_times):
            alog.atom_error(f"worker {i} error working process, result is 100")
            time.sleep(0.01)
    return i

def worker_raw(i, a_times=5):

    for _ in range(a_times):
        logger.error(f"worker {i} error working process, result is 100")
        time.sleep(0.01)


def worker_cross(i, a_times=5):
    with ALogger(logger) as alog:
        for _ in range(a_times):
            alog.atom_error(f"worker cross {i} error working process, result is 100")
            time.sleep(0.01)
    for _ in range(a_times):
        logger.info(f"worker cross {i} error working process")

def test_alogger():
    t_start = time.time_ns()
    fn = partial(worker, a_times=100)
    with ThreadPoolExecutor(max_workers=16) as excutor:
        res = list(excutor.map(fn, list(range(500))))
        print(len(res))
        print(res)


    logger.info(f"worker time escap : {(time.time_ns() - t_start) / 1_000_000_000}\n\n")


def test_alogger_raw():
    t_start = time.time_ns()
    fn = partial(worker_raw, a_times=100)
    with ThreadPoolExecutor(max_workers=16) as excutor:
        res = list(excutor.map(fn, list(range(500))))

    logger.info(f"worker_raw time escap : {(time.time_ns() - t_start) / 1_000_000_000}\n\n")

def test_alogger_cross():
    t_start = time.time_ns()
    fn = partial(worker_cross, a_times=100)
    with ThreadPoolExecutor(max_workers=16) as excutor:
        res = list(excutor.map(fn, list(range(500))))

    logger.info(f"worker_cross time escap : {(time.time_ns() - t_start) / 1_000_000_000}\n\n")


if __name__=="__main__":
    fire.Fire()