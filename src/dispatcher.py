"""
dispatcher.py定义了一个Dispatcher类，用于处理任务队列中的任务。

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : dispatcher.py
    @IDE     : VsCode
"""

# Standard Library
import copy
import time
import json
from queue import Queue
from pathlib import Path
from threading import RLock, Event
from concurrent.futures import ThreadPoolExecutor

# Third-Party Library
from loguru import logger

# My Library
from .pipeline import Pipeline

from utils.helper import filelock
from utils.helper import get_thread_id
from utils.helper import Task, Product


class Dispatcher:
    def __init__(self, cache_file: Path):
        logger.debug("Dispatcher 初始化")
        logger.debug("开始监控任务队列")

        self.lock: RLock = filelock
        self.cache_file = cache_file

    def dispatch(self, close_event: Event, queue: Queue[Task], pipeline: Pipeline):

        def handle_task(task: Task):
            tid = get_thread_id()
            logger.success(f"线程 {tid} 开始处理任务: {task.name}")
            final_product: Product = copy.deepcopy(pipeline).execute(task)

            if final_product.status == "success":
                logger.success(f"线程 {tid} 任务处理完成: {task.name}")
                with self.lock:
                    with self.cache_file.open("r", encoding="utf8") as f:
                        last_cache: list[dict[str, str | bool]] = json.load(f)

                        # 将task对应的状态修改为已处理, 并记录到缓存文件中
                        for task_cache in last_cache:
                            if task_cache["name"] == task.name:
                                task_cache["processed"] = True
                                break

                    with self.cache_file.open("w", encoding="utf8") as f:
                        json.dump(last_cache, f, ensure_ascii=False)
            return final_product

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            while not close_event.is_set():
                if queue.empty():
                    continue

                task: Task = queue.get()
                logger.debug(f"提交任务到线程池: {task.name}")
                future = executor.submit(handle_task, task)

                final_product: Product = future.result()
                if final_product.status == "success":
                    results.append(results)
                else:
                    logger.warning(f"任务处理失败: {task.name}, 重新添加到任务队列")
                    queue.put(task)

        return results
