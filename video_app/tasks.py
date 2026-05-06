import subprocess
from pathlib import Path

from django.conf import settings
from django_rq import job

from .models import Video


HLS_VARIANTS = (
    {"name": "480p", "height": 480, "bandwidth": 800000},
    {"name": "720p", "height": 720, "bandwidth": 2800000},
    {"name": "1080p", "height": 1080, "bandwidth": 5000000},
)


def get_video(video_id: int) -> Video | None:
    try:
        return Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return None


def run_ffmpeg_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def get_hls_output_dir(video: Video) -> Path:
    output_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_thumbnail_path(video: Video) -> Path:
    thumbnail_dir = Path(settings.MEDIA_ROOT) / "thumbnails"
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    return thumbnail_dir / f"video_{video.id}.jpg"


def create_thumbnail(source_path: Path, thumbnail_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:01",
        "-i",
        str(source_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(thumbnail_path),
    ]

    run_ffmpeg_command(command)


def get_hls_command(
    source_path: Path,
    playlist_path: Path,
    segment_path: Path,
    height: int,
) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-vf",
        f"scale=-2:{height}",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-g",
        "48",
        "-keyint_min",
        "48",
        "-sc_threshold",
        "0",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-hls_time",
        "6",
        "-hls_playlist_type",
        "vod",
        "-hls_segment_filename",
        str(segment_path),
        str(playlist_path),
    ]


def create_hls_variant(source_path: Path, output_dir: Path, variant: dict) -> list[str]:
    variant_name = variant["name"]
    playlist_path = output_dir / f"{variant_name}.m3u8"
    segment_path = output_dir / f"{variant_name}_%05d.ts"

    command = get_hls_command(
        source_path,
        playlist_path,
        segment_path,
        variant["height"],
    )

    run_ffmpeg_command(command)

    return [
        f"#EXT-X-STREAM-INF:BANDWIDTH={variant['bandwidth']}",
        f"{variant_name}.m3u8",
    ]


def create_master_playlist(source_path: Path, output_dir: Path) -> None:
    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

    for variant in HLS_VARIANTS:
        lines.extend(create_hls_variant(source_path, output_dir, variant))

    master_playlist_path = output_dir / "master.m3u8"
    master_playlist_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_video_paths(video: Video, thumbnail_path: Path) -> None:
    video.thumbnail = f"thumbnails/{thumbnail_path.name}"
    video.hls_master_playlist = f"hls/{video.id}/master.m3u8"
    video.save(update_fields=["thumbnail", "hls_master_playlist"])


@job("default", timeout=28800)
def process_video(video_id: int) -> None:
    video = get_video(video_id)

    if video is None:
        return

    source_path = Path(video.video_file.path)
    output_dir = get_hls_output_dir(video)
    thumbnail_path = get_thumbnail_path(video)

    create_thumbnail(source_path, thumbnail_path)
    create_master_playlist(source_path, output_dir)
    update_video_paths(video, thumbnail_path)