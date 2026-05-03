from .models import Video
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"New video created: {instance.title}")
    print(f"Video saved: {instance.title}")

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    print(f"Video deleted: {instance.title}")