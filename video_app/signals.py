from functools import partial

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import process_video
from .utils import delete_video_assets, get_hls_directory


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created: bool, **kwargs) -> None:
    if not created:
        return

    transaction.on_commit(lambda: process_video.delay(instance.id))


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs) -> None:
    video_name = instance.video_file.name
    thumbnail_name = instance.thumbnail.name if instance.thumbnail else ""
    hls_path = get_hls_directory(instance.id)

    delete_assets = partial(
        delete_video_assets,
        video_name,
        instance.video_file.storage,
        thumbnail_name,
        instance.thumbnail.storage,
        hls_path,
    )

    transaction.on_commit(delete_assets)