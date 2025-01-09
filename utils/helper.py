"""
工具函数

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : helper.py
    @IDE     : VsCode
"""

# Standard Library
import json
import base64
import quopri
from typing import Any
from pathlib import Path

# Third-Party Library

# Torch Library


# My Library
def read_json(json_path: Path) -> dict[str, Any]:
    """读取指定路径的 JSON 文件并将其内容解析为字典。验证文件存在后再进行读取操作。

    从指定路径读取 JSON 文件并将其转换为 Python 字典。在读取之前校验文件是否存在。

    Args:
        json_path: JSON 文件的路径。

    Returns:
        解析后的 JSON 数据字典。

    Raises:
        AssertionError: 如果指定的文件路径不存在。
    """

    assert json_path.exists(), f"文件路径不存在 {json_path}"

    with json_path.open(mode="r") as f:
        content = f.read()

    return json.loads(content)


def base64_decode(encrypted_str: str) -> bytes:
    return base64.urlsafe_b64decode(encrypted_str)


def quoted_printable_decode(encrypted_str: str) -> bytes:
    return quopri.decodestring(encrypted_str)


if __name__ == "__main__":
    jp = Path(__file__).resolve().parent.parent / "config/email.json"

    import pprint

    pprint.pprint(read_json(jp))