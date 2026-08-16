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
            "item_name": item.name,
        }
    )

    try:
        channel.create(str(buyer.id))
    except Exception:
        pass

    return channel

def send_donation_accepted_notification(item, receiver, donor):
    """Tell the requester their donation request was accepted"""
    client = get_stream_client()

    client.upsert_users([
        {"id": str(receiver.id), "name": receiver.username},
        {"id": str(donor.id), "name": donor.username},
    ])

    channel_id = f"item-{item.id}-{receiver.id}-{donor.id}"
    channel = client.channel(
        "messaging",
        channel_id,
        {
            "members": [str(receiver.id), str(donor.id)],
            "item_name": item.name,
        },
    )

    try:
        channel.create(str(donor.id))
    except Exception:
        pass

    channel.send_message(
        {
            "text": (
                f"Your request for '{item.name}' was accepted. "
                f"we can arrange the handover."
            ),
            "type": "system"
        },
        str(donor.id)
    )

    return channel
    
def send_auction_winner_notification(auction, winner):
    """Send notification to auction winner via Stream Chat"""
    client = get_stream_client()
    
    # Ensure users exist
    client.upsert_users([
        {
            "id": str(winner.id),
            "name": winner.username,
        },
        {
            "id": str(auction.item.owner.id),
            "name": auction.item.owner.username,
        }
    ])
    
    # Use existing item channel or create new one
    channel_id = f"item-{auction.item.id}-{winner.id}-{auction.item.owner.id}"
    channel = client.channel(
        "messaging",
        channel_id,
        {
            "members": [
                str(winner.id),
                str(auction.item.owner.id),
            ],
            "item_name": auction.item.name,
        }
    )
    
    # Create channel if it doesn't exist
    try:
        channel.create(str(auction.item.owner.id))
    except Exception:
        pass
    
    # Send auction win message
    highest_bid = auction.bids.order_by('-bid_amount').first()
    channel.send_message(
        {
            "text": f"Congratulations! You won the auction for '{auction.item.name}' with a bid of {highest_bid.bid_amount} SYP",
            "type": "system"
        },
        str(auction.item.owner.id)
    )
    
    return channel