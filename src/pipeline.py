"""
pipeline.py定义了一个Pipeline类，用于将多个函数串联起来，形成一个处理流程。

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : pipeline.py
    @IDE     : VsCode
"""

# Standard Library
from typing import Any, Optional
from collections.abc import Callable


class Pipeline:
    def __init__(self, pipes: Optional[list[Callable]] = None):
        if pipes is None:
            pipes = []
        self.pipes: list[Callable] = pipes

    def add_pipes(self, step: list[Callable] | Callable) -> "Pipeline":
        if isinstance(step, list):
            self.pipes.extend(step)
        elif callable(step):
            self.pipes.append(step)
        return self

    def execute(self, data: Any) -> Any:
        for pipe in self.pipes:
            data = pipe(data)
        return data
