"""
Bypy自动下载视频

    @Time    : 2024/12/27
    @Author  : JackWang
    @File    : download.py
    @IDE     : VsCode
"""

# Standard Library
import subprocess
from pathlib import Path

# Third-Party Library
import bypy

# My Library
from utils.logger import logger
from utils.helper import Product
from utils.helper import get_thread_id, get_relative_path


def get_dir_files(remote_path: str):
    result = subprocess.run(
        ["bypy", "list", remote_path], capture_output=True, text=True
    )

    return [line.split(" ")[1] for line in result.stdout.splitlines()[1:]]


def download_dir(product: Product) -> Product:
    output_dir: Path = product.output_dir
    remote_path: Path = product.remote_path

    base_dir = output_dir / remote_path.parts[-1]
    base_dir.mkdir(exist_ok=True, parents=True)

    mp4_path = None
    for file in (filelist := get_dir_files(remote_path)):

        if not file.endswith(".mp4"):
            continue

        mp4_path = base_dir / file
        download_file = f"{base_dir}/{file}"
        logger.success(
            f"线程 {get_thread_id()} 开始下载文件: {file} -> {get_relative_path(download_file)}"
        )
        subprocess.run(
            ["bypy", "downfile", f"{remote_path}/{file}", download_file],
            capture_output=True,
            text=True,
        )

    product.status = "failed" if mp4_path is None else "downloaded"

    product.filelist = filelist
    product.base_dir = base_dir
    product.mp4_path = mp4_path

    return product
