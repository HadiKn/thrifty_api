from django.urls import path
from .views import StreamTokenView,ItemChatView

urlpatterns = [
    path("token/", StreamTokenView.as_view()),
    path("items/<int:item_id>/", ItemChatView.as_view()),
]
