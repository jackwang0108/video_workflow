"""
watcher.py定义了一个Watcher类，用于监控百度网盘指定目录下的文件变化。

当文件发生变换的时候, 将作为生产者向任务队列中添加任务。

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : watcher.py
    @IDE     : VsCode
"""

# Standard Library
import time
import json
import pprint
import subprocess
from queue import Queue
from pathlib import Path
from threading import RLock, Event

# Third-Party Library
import bypy
from loguru import logger

# My Library
from .types import Task
from .common import filelock


class Watcher:
    def __init__(
        self,
        cache_file: Path,
        remote_path: Path = Path("上传视频/待处理"),
    ):
        logger.debug("Watcher 初始化")
        logger.info(f"开始监控百度网盘路径: {remote_path}")

        self.lock: RLock = filelock
        self.cache: list[dict[str, str | bool]] = []
        self.cache_file: Path = cache_file

        self.remote_path = remote_path

    def get_files(self) -> list[str]:
        result = subprocess.run(
            ["bypy", "list", str(self.remote_path)], capture_output=True, text=True
        )
        return [line.split(" ")[1] for line in result.stdout.splitlines()[1:]]

    def get_tasks(self) -> list[Task]:
        files = self.get_files()

        return [
            Task(name=file, remote_path=self.remote_path / file)
            for file in files
            if all(file != processed_record["name"] for processed_record in self.cache)
        ]

    def watch(self, close_event: Event, task_queue: Queue[Task]):
        while not close_event.is_set():
            # 读取缓存
            if self.cache_file.exists():
                with self.lock:
                    with self.cache_file.open("r", encoding="utf8") as f:
                        last_caches = json.load(f)

                self.cache.extend(
                    record for record in last_caches if record["processed"]
                )

            # 获取新任务
            new_tasks = self.get_tasks()

            if len(new_tasks) == 0:
                logger.debug(
                    f"没有新任务, 当前队列任务数 {task_queue.qsize()}, 10秒后重新检查..."
                )
                time.sleep(10)
                continue

            # 更新缓存
            for task in new_tasks:
                self.cache.append(
                    {
                        "name": task.name,
                        "remote_path": str(task.remote_path),
                        "processed": False,
                    }
                )

            with self.lock:
                with self.cache_file.open("w", encoding="utf8") as f:
                    json.dump(self.cache, f, ensure_ascii=False)

            # 添加任务到任务队列
            for task in new_tasks:
                logger.info(f"添加任务: {task.name}")
                task_queue.put(task)

            # 输出目前正在排队的任务
            if task_queue.qsize() > 0:
                logger.success(f"当前队列任务数: {task_queue.qsize()}")

            time.sleep(10)


if __name__ == "__main__":
    watcher = Watcher()
    watcher.watch()
