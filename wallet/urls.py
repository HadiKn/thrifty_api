from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.WalletDetailView.as_view(), name='wallet-detail'),
    path('transactions/', views.WalletTransactionListView.as_view(), name='wallet-transactions'),
    path('topup/', views.wallet_topup, name='wallet-topup'),
    path('topup/<int:user_id>/', views.wallet_topup, name='wallet-topup-user'),
]
