"""
main.py 程序入口

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : main.py
    @IDE     : VsCode
"""

# Standard Library
import datetime
import threading
from queue import Queue
from pathlib import Path

# Third-Party Library
from worker import abort_all_thread


# My Library
from utils.logger import get_logger
from src.watcher import Watcher
from src.pipeline import Pipeline
from src.dispatcher import Dispatcher


def print_data(data):
    print(data)
    return data


def main():
    log_dir = (
        Path(__file__).resolve().parent
        / f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    log_dir.mkdir(exist_ok=True, parents=True)

    logger = get_logger(log_file=log_dir / "running.log")
    logger.info("程序启动")

    task_queue = Queue()
    watcher = Watcher(log_dir=log_dir)
    dispatcher = Dispatcher(queue=task_queue)

    threading.Thread(target=watcher.watch, args=(task_queue,)).start()
    threading.Thread(target=dispatcher.dispatch).start()

    watcher_thread = threading.Thread(target=watcher.watch, args=(task_queue,))
    dispatcher_thread = threading.Thread(target=dispatcher.dispatch)

    watcher_thread.name = "Watcher"
    watcher_thread.start()

    dispatcher_thread.name = "Dispatcher"
    dispatcher_thread.start()

    try:
        watcher_thread.join()
        dispatcher_thread.join()
    except KeyboardInterrupt:
        logger.info("程序退出")
        abort_all_thread()
        exit(0)


if __name__ == "__main__":
    main()
