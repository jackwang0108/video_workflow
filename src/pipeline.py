"""
pipeline.py定义了一个Pipeline类，用于将多个函数串联起来，形成一个处理流程。

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : pipeline.py
    @IDE     : VsCode
"""

# Standard Library
from typing import Any
from collections.abc import Callable


class Pipeline:
    def __init__(self):
        self.steps: list[Callable] = []

    def add_step(self, step: Callable) -> "Pipeline":
        self.steps.append(step)
        return self

    def execute(self, data: Any) -> Any:
        for step in self.steps:
            data = step(data)
        return data
