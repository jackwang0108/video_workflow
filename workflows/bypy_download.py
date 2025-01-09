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
from utils.helper import get_thread_id
from utils.helper import Product


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

    for file in (filelist := get_dir_files(remote_path)):

        if file.endswith(".mp4"):
            mp4_path = base_dir / file

        download_file = f"{base_dir}/{file}"
        logger.success(
            f"线程 {get_thread_id()} 开始下载文件: {file} -> {download_file}"
        )
        subprocess.run(
            ["bypy", "downfile", f"{remote_path}/{file}", download_file],
            capture_output=True,
            text=True,
        )

    product.filelist = filelist
    product.status = "downloaded"
    product.base_dir = base_dir
    product.mp4_path = Path(mp4_path)

    return product
