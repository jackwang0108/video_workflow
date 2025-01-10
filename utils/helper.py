"""
helper.py 提供了一系列工具函数

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : helper.py
    @IDE     : VsCode
"""

# Standard Library
import json
import base64
import quopri
import threading
import subprocess
from pathlib import Path
from typing import Any, Optional

# Third-Party Library
from pydantic import BaseModel

filelock = threading.Lock()


class Task(BaseModel):
    name: str
    remote_path: Path

    output_dir: Path = Path(__file__).resolve().parent.parent / "data"


class Product(BaseModel):
    class Config:
        extra = "allow"

    name: str = ""
    status: str = ""
    output_dir: Optional[Path] = None
    remote_path: Optional[Path] = None

    # bypy_download
    base_dir: Optional[Path] = None
    mp4_path: Optional[Path] = None
    filelist: Optional[list[str]] = None

    # process_videos
    clip_dir: Optional[Path] = None
    clip_files: Optional[list[Path]] = None
    audio_files: Optional[list[Path]] = None

    # extract_srt
    zh_srt_files: Optional[list[Path]] = None
    en_srt_files: Optional[list[Path]] = None


def get_thread_id() -> int:
    return threading.get_native_id()


def get_free_gpu_indices():

    def run_cmd(cmd):
        out = (subprocess.check_output(cmd, shell=True)).decode("utf-8")[:-1]
        return out

    out = run_cmd("nvidia-smi -q -d Memory | grep -A4 GPU")
    out = (out.split("\n"))[1:]
    out = [l for l in out if "--" not in l]

    total_gpu_num = int(len(out) / 5)
    gpu_bus_ids = []
    for i in range(total_gpu_num):
        gpu_bus_ids.append([l.strip().split()[1] for l in out[i * 5 : i * 5 + 1]][0])

    out = run_cmd("nvidia-smi --query-compute-apps=gpu_bus_id --format=csv")
    gpu_bus_ids_in_use = (out.split("\n"))[1:]
    gpu_ids_in_use = []

    for bus_id in gpu_bus_ids_in_use:
        gpu_ids_in_use.append(gpu_bus_ids.index(bus_id))

    return [i for i in range(total_gpu_num) if i not in gpu_ids_in_use]


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
