from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance: Video, created: bool, **kwargs) -> None:
    if created:
        print(f"New video created: {instance.title}")
        return
    print(f"Video saved: {instance.title}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance: Video, **kwargs) -> None:
    def delete_files() -> None:
        instance.video_file.delete(save=False)
        instance.thumbnail.delete(save=False)
    transaction.on_commit(delete_files)
    print(f"Video deleted: {instance.title}")