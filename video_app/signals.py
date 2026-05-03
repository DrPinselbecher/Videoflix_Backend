from pathlib import PurePosixPath

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
import django_rq

from .models import Video
from .tasks import convert_video


VIDEO_RESOLUTIONS = (480, 720, 1080)


def get_video_variant_names(file_name: str) -> list[str]:
    path = PurePosixPath(file_name)

    return [
        str(path.with_name(f"{path.stem}_{resolution}p{path.suffix}"))
        for resolution in VIDEO_RESOLUTIONS
    ]


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created: bool, **kwargs) -> None:
    if not created:
        print(f"Video saved: {instance.title}")
        return

    def enqueue_jobs() -> None:
        queue = django_rq.get_queue("default")

        for resolution in VIDEO_RESOLUTIONS:
            queue.enqueue(convert_video, instance.video_file.path, resolution)

    transaction.on_commit(enqueue_jobs)

    print(f"New video created: {instance.title}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs) -> None:
    video_name = instance.video_file.name
    thumbnail_name = instance.thumbnail.name

    video_storage = instance.video_file.storage
    thumbnail_storage = instance.thumbnail.storage

    def delete_files() -> None:
        for variant_name in get_video_variant_names(video_name):
            if video_storage.exists(variant_name):
                video_storage.delete(variant_name)

        if video_name and video_storage.exists(video_name):
            video_storage.delete(video_name)

        if thumbnail_name and thumbnail_storage.exists(thumbnail_name):
            thumbnail_storage.delete(thumbnail_name)

    transaction.on_commit(delete_files)

    print(f"Video deleted: {instance.title}")