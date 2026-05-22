from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from chat.services import get_stream_client

User = get_user_model()


@receiver(post_save, sender=User)
def create_stream_user(sender, instance, created, **kwargs):

    if created:
        client = get_stream_client()

        client.upsert_user({
            "id": str(instance.id),
            "name": instance.username,
        })
