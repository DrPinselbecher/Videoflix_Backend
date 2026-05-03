# video_app/tasks.py

import subprocess
from pathlib import Path


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