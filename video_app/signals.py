import shutil
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import process_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created: bool, **kwargs) -> None:
    if not created:
        return

    def enqueue_job() -> None:
        process_video.delay(instance.id)

    transaction.on_commit(enqueue_job)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs) -> None:
    video_name = instance.video_file.name
    thumbnail_name = instance.thumbnail.name

    video_storage = instance.video_file.storage
    thumbnail_storage = instance.thumbnail.storage
    hls_path = Path(settings.MEDIA_ROOT) / "hls" / str(instance.id)

    def delete_files() -> None:
        if video_name and video_storage.exists(video_name):
            video_storage.delete(video_name)

        if thumbnail_name and thumbnail_storage.exists(thumbnail_name):
            thumbnail_storage.delete(thumbnail_name)

        if hls_path.exists():
            shutil.rmtree(hls_path)

    transaction.on_commit(delete_files)