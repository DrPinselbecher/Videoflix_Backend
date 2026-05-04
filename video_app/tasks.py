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


@job("default", timeout="8h")
def process_video(video_id: int) -> None:
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return

    source_path = Path(video.video_file.path)
    output_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video.id)
    output_dir.mkdir(parents=True, exist_ok=True)

    master_playlist_lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
    ]

    for variant in HLS_VARIANTS:
        variant_name = variant["name"]
        playlist_path = output_dir / f"{variant_name}.m3u8"
        segment_path = output_dir / f"{variant_name}_%05d.ts"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-vf",
            f"scale=-2:{variant['height']}",
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

        subprocess.run(cmd, check=True)

        master_playlist_lines.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH={variant['bandwidth']}"
        )
        master_playlist_lines.append(f"{variant_name}.m3u8")

    master_playlist_path = output_dir / "master.m3u8"
    master_playlist_path.write_text(
        "\n".join(master_playlist_lines) + "\n",
        encoding="utf-8",
    )

    video.hls_master_playlist = f"hls/{video.id}/master.m3u8"
    video.save(update_fields=["hls_master_playlist"])