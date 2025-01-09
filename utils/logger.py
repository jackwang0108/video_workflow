"""
logger.py 提供了 项目的日志输出工具

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : logger.py
    @IDE     : VsCode
"""

# Standard Library
import sys
from pathlib import Path

# Third-Party Library
from loguru import logger

# Torch Library


# My Library
def get_logger(log_file: Path, with_time: bool = True):
    global logger

    logger.remove()

    # file handler
    logger.add(
        log_file,
        level="DEBUG",
        rotation="100 MB",
        format=f"{'{time:YYYY-D-MMMM@HH:mm:ss}' if with_time else ''}│ {{module:<10}} │ {{message}}",
    )

    # terminal handler
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=f"{'<green>{time:YYYY-D-MMMM@HH:mm:ss}</green>' if with_time else ''}│ <fg #ec6337><bold>{{module:<10}}</bold></fg #ec6337> │ <level>{{message}}</level>",
        filter=lambda record: record["module"] == "watcher",
    )

    logger.add(
        sys.stderr,
        level="DEBUG",
        format=f"{'<green>{time:YYYY-D-MMMM@HH:mm:ss}</green>' if with_time else ''}│ <fg #4daab3><bold>{{module:<10}}</bold></fg #4daab3> │ <level>{{message}}</level>",
        filter=lambda record: record["module"] == "dispatcher",
    )

    logger.add(
        sys.stderr,
        level="DEBUG",
        format=f"{'<green>{time:YYYY-D-MMMM@HH:mm:ss}</green>' if with_time else ''}│ {{module:<10}} │ <level>{{message}}</level>",
        filter=lambda record: record["module"] not in ["watcher", "dispatcher"],
    )

    return logger
