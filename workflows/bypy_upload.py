"""
bypy_upload.py 提供了上传文件到百度云的功能

    @Time    : 2025/01/10
    @Author  : JackWang
    @File    : bypy_upload.py
    @IDE     : VsCode
"""

# Standard Library
from pathlib import Path

# Third-Party Library
from bypy import ByPy

# My Library
from utils.logger import logger
from utils.helper import Product, get_thread_id, get_relative_path


def upload_dir(product: Product) -> Product:

    if product.status == "failed":
        return product

    bypy = ByPy(verify=False)

    logger.success(
        f"线程 {get_thread_id()} 开始上传本地文件夹 {get_relative_path(product.clip_dir)} -> {product.remote_path}/clips"
    )
    bypy.mkdir(f"{product.remote_path}/clips")

    for dir in product.clip_dir.iterdir():

        remote_dir = f"{product.remote_path}/clips/{dir.parts[-1]}"

        logger.success(
            f"线程 {get_thread_id()} 开始上传文件夹: {get_relative_path(dir)} -> {remote_dir}"
        )

        bypy.mkdir(remote_dir)

        bypy.syncup(str(dir), str(remote_dir))

        logger.success(
            f"线程 {get_thread_id()} 上传文件夹完成: {get_relative_path(dir)} -> {remote_dir}"
        )

    product.status = "success"

    return product
