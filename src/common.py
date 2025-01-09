"""
common.py 提供了主程序中可能用到的一些通用函数。

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : common.py
    @IDE     : VsCode
"""

# Standard Library
import ctypes
import threading

filelock = threading.Lock()


def get_thread_id() -> int:
    return ctypes.CDLL("libc.so.6").syscall(186)
