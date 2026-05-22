from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.services import get_stream_client


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from items.models import Item
from .services import create_item_channel


class ItemChatView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        item = Item.objects.get(id=item_id)

        buyer = request.user
        seller = item.owner

        channel = create_item_channel(item, buyer, seller)

        return Response({
            "channel_id": channel.id
        })


class StreamTokenView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        client = get_stream_client()

        token = client.create_token(str(request.user.id))

        return Response({
            "token": token,
            "user_id": str(request.user.id),
            "api_key": client.api_key,
        })