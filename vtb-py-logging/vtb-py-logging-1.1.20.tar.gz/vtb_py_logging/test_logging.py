import asyncio
import contextvars
import logging
import log_extra
import threading
import functools
import os
from configure import initialize_logging
from vtb_py_logging.log_config import LogConfigure

LOGGER = logging.getLogger(__name__)


def log_in_thread(name):
    LOGGER.info("log_in_thread %s", name)
    with log_extra.log_extra(request_id=f"lll-{name}"):
        LOGGER.info("log_in_thread %s", name)
    LOGGER.info("log_in_thread after %s", name)


async def alog3(name):
    LOGGER.info("async log3 %s", name)


async def alog2(name):
    LOGGER.info("async log2 %s", name)
    await asyncio.Task(alog3(name))


async def alog(name):
    LOGGER.info("async log %s", name)
    await alog2(name)


def test_inh():
    class Base:
        def before(self):
            pass

    class A(Base):
        def before(self):
            super().before()
            print("A.before")

    class B(Base):
        def before(self):
            print("B.before")
            super().before()

    class C(Base):
        def before(self):
            print("C.before", super())
            super().before()

    class D(A):
        def before(self):
            print("D.before")
            super().before()

    class E(D, B, C):
        pass

    print(C.mro())
    print(C().before())

    print(E.mro())
    E().before()


def main():
    test_inh()
    os.environ["LOG_SQL"] = "True"

    log_extra.init_extra_logger()
    log_extra.init_extra_logger()
    log_extra.init_extra_logger()
    config = LogConfigure(json_multiline=True, app_name="acc")
    initialize_logging(config=config)
    logging.info("root info %(rrr)s", {"rrr": "aaa"})
    with log_extra.log_extra(request_id="r-xxxxx", progname="log-test"):
        logging.info("root2 info")
        logging.debug("log debug")
        logging.warning("log warning")
        logging.error("log error")
        try:
            1 // 0
        except:
            logging.exception("log exc")

        with log_extra.log_extra(request_id="r-yyyy", zzz="vvv"):
            logger = logging.getLogger("django.db.backends")
            logger.warning("xxxxxxxxxxxxxx",
                         extra={
                             "duration": 0.123,
                             "sql": "Select distinct Salary from Employee e1 where 2=Select count(distinct Salary) from Employee e2 where e1.salary<=e2.salary;",
                             "params": {"xxx": "yyy"}
                         }
                         )

            logging.info("where are my extra")
            ctx = contextvars.copy_context()
            thread1 = threading.Thread(target=ctx.run, args=(functools.partial(log_in_thread, "first"), ))
            thread1.start()
            thread1.join()

    logging.info("last root info")

    ctx = contextvars.copy_context()
    thread2 = threading.Thread(target=ctx.run, args=(functools.partial(log_in_thread, "second"),))
    thread2.start()
    thread2.join()

    asyncio.run(alog("11112"))

    with log_extra.log_extra(request_id="r-aaaaa"):
        asyncio.run(alog("22"))


main()
