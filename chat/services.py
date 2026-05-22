from stream_chat import StreamChat
from django.conf import settings


def get_stream_client():
    return StreamChat(
        api_key=settings.STREAM_API_KEY,
        api_secret=settings.STREAM_API_SECRET,
    )

def create_item_channel(item, buyer, seller):

    client = get_stream_client()

    # Ensure users exist
    client.upsert_users([
        {
            "id": str(buyer.id),
            "name": buyer.username,
        },
        {
            "id": str(seller.id),
            "name": seller.username,
        }
    ])

    channel_id = f"item-{item.id}-{buyer.id}-{seller.id}"

    channel = client.channel(
        "messaging",
        channel_id,
        {
            "members": [
                str(buyer.id),
                str(seller.id),
            ],
        }
    )

    try:
        channel.create(str(buyer.id))
    except Exception:
        pass

    return channel