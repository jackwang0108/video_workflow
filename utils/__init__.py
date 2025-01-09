"""
工具函数库

    @Time    : 2024/12/27
    @Author  : JackWang
    @File    : helper.py
    @IDE     : VsCode
"""

# Third-Party Library
from pydantic import BaseModel


class VideoInfo(BaseModel):
    From: str
    To: str
    Subject: str
    Content: str
