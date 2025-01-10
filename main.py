"""
main.py 程序入口

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : main.py
    @IDE     : VsCode
"""

# Standard Library
import time
import datetime
import threading
from queue import Queue
from pathlib import Path

# Third-Party Library
from worker import abort_all_thread


# My Library
from utils.logger import get_logger
from utils.helper import Task
from src.watcher import Watcher
from src.pipeline import Pipeline
from src.dispatcher import Dispatcher

from workflows.bypy_download import download_dir
from workflows.create_product import create_product
from workflows.process_videos import process_video
from workflows.extract_srt import extract_srt
from workflows.bypy_upload import upload_dir


def print_data(data):
    print(data)
    return {"status": "success"}


def setup_logger(log_dir: Path = Path(__file__).resolve().parent / "logs"):
    log_dir.mkdir(exist_ok=True, parents=True)
    log_file = (
        log_dir / f"running-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )

    return log_dir, get_logger(log_file)


def main():
    log_dir, logger = setup_logger()

    task_queue: Queue[Task] = Queue()

    cache_file = log_dir / "cache.json"
    watcher = Watcher(cache_file=cache_file)
    dispatcher = Dispatcher(cache_file=cache_file)

    close_event = threading.Event()

    pipeline = Pipeline(
        [
            create_product,
            download_dir,
            process_video,
            extract_srt,
            upload_dir,
        ]
    )

    threads = [
        threading.Thread(
            target=watcher.watch,
            args=(close_event, task_queue),
        ),
        threading.Thread(
            target=dispatcher.dispatch,
            args=(close_event, task_queue, pipeline),
        ),
    ]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        close_event.set()
        logger.info("程序退出")


if __name__ == "__main__":
    main()
