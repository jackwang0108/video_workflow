"""
对视频进行编辑

    @Time    : 2024/12/28
    @Author  : JackWang
    @File    : edit_video.py
    @IDE     : VsCode
"""

# Standard Library
from pathlib import Path
from typing import Optional

# Third-Party Library
from loguru import logger
from proglog import ProgressBarLogger
from moviepy import VideoFileClip, VideoClip


# My Library
from utils.helper import Product, get_thread_id, get_relative_path


class MyBarLogger(ProgressBarLogger):

    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        pass

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called
        percentage = (value / self.bars[bar]["total"]) * 100
        if percentage % 10 == 0:
            logger.success(
                "线程 {thread_id} 进度: {percentage:.2f}%",
                thread_id=get_thread_id(),
                percentage=percentage,
            )


process_logger = MyBarLogger()


def load_video(mp4_path: Path) -> VideoFileClip:
    assert mp4_path.exists(), f"文件路径不存在{mp4_path}"

    return VideoFileClip(mp4_path)


def cut_clips(
    video: VideoFileClip,
    clip_dir: Path,
    start: Optional[int] = 0,
    end: Optional[int] = -1,
    step: Optional[int] = 8 * 60,
) -> list[Path]:
    if end == -1:
        end = int(video.duration)

    times = list(range(start, end, step))
    if end not in times:
        times.append(end)

    filename = Path(video.filename)
    clip_dir.mkdir(parents=True, exist_ok=True)
    clip_files = []
    for idx, (start, end) in enumerate(zip(times[:-1], times[1:])):

        outfile = clip_dir / f"片段-{idx}" / f"{filename.stem}-{idx}{filename.suffix}"
        outfile.parent.mkdir(parents=True, exist_ok=True)

        logger.success(
            f"线程 {get_thread_id()} 视频片段: {idx} -> {get_relative_path(outfile)}"
        )

        clip_files.append(outfile)
        if outfile.exists():
            continue

        clip: VideoClip = video.subclipped(start, end)

        clip.write_videofile(outfile, audio=True, threads=16)

    return clip_files


def extract_audio(clip_files: list[Path]) -> list[Path]:

    audio_files = []
    for idx, video_file in enumerate(clip_files):

        audio_file = video_file.with_suffix(".mp3")

        audio_files.append(audio_file)
        if audio_file.exists():
            continue

        logger.success(
            f"线程 {get_thread_id()} 提取音频文件: {idx} -> {get_relative_path(audio_file)}"
        )

        clip = VideoFileClip(video_file)
        clip.audio.write_audiofile(audio_file)

    return audio_files


def process_video(product: Product) -> Product:

    if product.status == "failed":
        return product

    logger.success(f"线程 {get_thread_id()} 开始处理视频文件: {product.mp4_path}")

    video = load_video(product.mp4_path)

    clip_dir = product.base_dir / "clips"

    clip_files = cut_clips(video, clip_dir)
    audio_files = extract_audio(clip_files)

    product.status = "processed"
    product.clip_dir = clip_dir
    product.clip_files = clip_files
    product.audio_files = audio_files

    return product
