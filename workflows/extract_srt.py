"""
extract_srt.py 从音频文件中提取字幕

    @Time    : 2025/01/10
    @Author  : JackWang
    @File    : extract_srt.py
    @IDE     : VsCode
"""

# Standard Library
import subprocess
from pathlib import Path

# Third-Party Library

# My Library
from utils.logger import logger
from utils.helper import Product
from utils.helper import get_free_gpu_indices, get_thread_id, get_relative_path


def extract_srt(product: Product) -> Product:
    # sourcery skip: extract-method

    if product.status == "failed":
        return product

    clip_files = product.clip_files

    while len(gpu_indices := get_free_gpu_indices()) == 0:
        continue

    device = f"cuda:{gpu_indices[0]}"

    zh_srt_files = [
        clip_file.with_name(f"{clip_file.stem}-zh.srt") for clip_file in clip_files
    ]
    en_srt_files = [
        clip_file.with_name(f"{clip_file.stem}-en.srt") for clip_file in clip_files
    ]

    clip_file: Path
    for clip_file, zh_srt_file, en_srt_file in zip(
        clip_files, zh_srt_files, en_srt_files
    ):

        # get zh srt
        logger.success(
            f"线程 {get_thread_id()} 提取中文字幕: {clip_file.name} -> {get_relative_path(zh_srt_file)}"
        )
        if not zh_srt_file.exists():
            subprocess.run(
                [
                    "subtitle",
                    "-t",
                    str(clip_file),
                    "--whisper-model",
                    "large-v2",
                    "--device",
                    f"{device}",
                    "--lang",
                    "zh",
                    "--target-lang",
                    "zh",
                ],
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["mv", f"{clip_file.with_suffix('.srt')}", f"{zh_srt_file}"],
            )

        logger.success(
            f"线程 {get_thread_id()} 提取英文字幕: {clip_file.name} -> {get_relative_path(en_srt_file)}"
        )

        if not en_srt_file.exists():
            subprocess.run(
                [
                    "subtitle",
                    "-tl",
                    str(clip_file),
                    "--whisper-model",
                    "large-v2",
                    "--device",
                    f"{device}",
                    "--target-lang",
                    "en",
                    "--China",
                ],
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["mv", f"{clip_file.with_suffix('.srt')}", f"{en_srt_file}"],
            )

    product.status = "extracted"
    product.zh_srt_files = zh_srt_files
    product.en_srt_files = en_srt_files

    return product
