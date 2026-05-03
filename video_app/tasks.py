# video_app/tasks.py

import subprocess
from pathlib import Path

from django_rq import job

from .models import Video


VIDEO_RESOLUTIONS = (480, 720, 1080)


def convert_video(source: str, resolution: int) -> None:
    source_path = Path(source)
    target_path = source_path.with_name(
        f"{source_path.stem}_{resolution}p{source_path.suffix}"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-vf",
        f"scale=-2:{resolution}",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-preset",
        "medium",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(target_path),
    ]

    subprocess.run(cmd, check=True)


@job("default", timeout=28800)
def process_video(video_id: int) -> None:
    video = Video.objects.get(id=video_id)
    video_path = video.video_file.path

    for resolution in VIDEO_RESOLUTIONS:
        convert_video(video_path, resolution)