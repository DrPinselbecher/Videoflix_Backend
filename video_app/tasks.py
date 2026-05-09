from pathlib import Path

from django_rq import job

from .utils import (
    create_master_playlist,
    create_thumbnail,
    get_hls_directory,
    get_thumbnail_path,
    get_video,
    update_video_paths,
)


@job("default", timeout=28800)
def process_video(video_id: int) -> None:
    """Generate thumbnail and HLS files for a video in the background."""
    video = get_video(video_id)

    if video is None:
        return

    source_path = Path(video.video_file.path)
    output_dir = get_hls_directory(video.id, create=True)
    thumbnail_path = get_thumbnail_path(video.id)

    create_thumbnail(source_path, thumbnail_path)
    create_master_playlist(source_path, output_dir)
    update_video_paths(video, thumbnail_path)