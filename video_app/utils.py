import shutil
import subprocess
from pathlib import Path
from typing import TypedDict

from django.conf import settings
from django.core.files.storage import Storage

from .models import Video


class HlsVariant(TypedDict):
    name: str
    height: int
    bandwidth: int


HLS_VARIANTS: tuple[HlsVariant, ...] = (
    {"name": "480p", "height": 480, "bandwidth": 800000},
    {"name": "720p", "height": 720, "bandwidth": 2800000},
    {"name": "1080p", "height": 1080, "bandwidth": 5000000},
)

HLS_RESOLUTIONS = tuple(variant["name"] for variant in HLS_VARIANTS)
HLS_PLAYLIST_CONTENT_TYPE = "application/vnd.apple.mpegurl"
HLS_SEGMENT_CONTENT_TYPE = "video/MP2T"


def get_video(video_id: int) -> Video | None:
    try:
        return Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return None


def is_valid_hls_resolution(resolution: str) -> bool:
    return resolution in HLS_RESOLUTIONS


def is_valid_hls_segment(resolution: str, segment: str) -> bool:
    return (
        segment.endswith(".ts")
        and "/" not in segment
        and "\\" not in segment
        and segment.startswith(f"{resolution}_")
    )


def get_hls_directory(video_id: int, create: bool = False) -> Path:
    hls_directory = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)

    if create:
        hls_directory.mkdir(parents=True, exist_ok=True)

    return hls_directory


def get_hls_playlist_path(movie_id: int, resolution: str) -> Path:
    return get_hls_directory(movie_id) / f"{resolution}.m3u8"


def get_hls_segment_path(movie_id: int, segment: str) -> Path:
    return get_hls_directory(movie_id) / segment


def get_thumbnail_path(video_id: int) -> Path:
    thumbnail_directory = Path(settings.MEDIA_ROOT) / "thumbnails"
    thumbnail_directory.mkdir(parents=True, exist_ok=True)
    return thumbnail_directory / f"video_{video_id}.jpg"


def run_ffmpeg_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def build_thumbnail_command(source_path: Path, thumbnail_path: Path) -> list[str]:
    return [
        "ffmpeg", "-y", "-ss", "00:00:01", "-i", str(source_path),
        "-frames:v", "1", "-q:v", "2", str(thumbnail_path),
    ]


def create_thumbnail(source_path: Path, thumbnail_path: Path) -> None:
    command = build_thumbnail_command(source_path, thumbnail_path)
    run_ffmpeg_command(command)


def get_hls_video_options(height: int) -> list[str]:
    return [
        "-vf", f"scale=-2:{height}", "-c:v", "libx264",
        "-preset", "medium", "-crf", "23",
    ]


def get_hls_keyframe_options() -> list[str]:
    return ["-g", "48", "-keyint_min", "48", "-sc_threshold", "0"]


def get_hls_audio_options() -> list[str]:
    return ["-c:a", "aac", "-b:a", "128k"]


def get_hls_output_options(segment_path: Path, playlist_path: Path) -> list[str]:
    return [
        "-hls_time", "6", "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(segment_path), str(playlist_path),
    ]


def build_hls_command(
    source_path: Path,
    playlist_path: Path,
    segment_path: Path,
    height: int,
) -> list[str]:
    command = ["ffmpeg", "-y", "-i", str(source_path)]
    command += get_hls_video_options(height)
    command += get_hls_keyframe_options()
    command += get_hls_audio_options()
    command += get_hls_output_options(segment_path, playlist_path)
    return command


def create_hls_variant(source_path: Path, output_dir: Path, variant: HlsVariant) -> list[str]:
    variant_name = variant["name"]
    playlist_path = output_dir / f"{variant_name}.m3u8"
    segment_path = output_dir / f"{variant_name}_%05d.ts"

    command = build_hls_command(
        source_path,
        playlist_path,
        segment_path,
        variant["height"],
    )

    run_ffmpeg_command(command)
    return [f"#EXT-X-STREAM-INF:BANDWIDTH={variant['bandwidth']}", f"{variant_name}.m3u8"]


def create_master_playlist(source_path: Path, output_dir: Path) -> None:
    playlist_lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

    for variant in HLS_VARIANTS:
        playlist_lines.extend(create_hls_variant(source_path, output_dir, variant))

    master_playlist_path = output_dir / "master.m3u8"
    master_playlist_path.write_text("\n".join(playlist_lines) + "\n", encoding="utf-8")


def update_video_paths(video: Video, thumbnail_path: Path) -> None:
    video.thumbnail = f"thumbnails/{thumbnail_path.name}"
    video.hls_master_playlist = f"hls/{video.id}/master.m3u8"
    video.save(update_fields=["thumbnail", "hls_master_playlist"])


def delete_stored_file(storage: Storage, file_name: str | None) -> None:
    if file_name and storage.exists(file_name):
        storage.delete(file_name)


def delete_hls_directory(hls_path: Path) -> None:
    if hls_path.exists():
        shutil.rmtree(hls_path)


def delete_video_assets(
    video_name: str,
    video_storage: Storage,
    thumbnail_name: str,
    thumbnail_storage: Storage,
    hls_path: Path,
) -> None:
    delete_stored_file(video_storage, video_name)
    delete_stored_file(thumbnail_storage, thumbnail_name)
    delete_hls_directory(hls_path)