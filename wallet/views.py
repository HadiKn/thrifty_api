from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wallet, WalletTransaction
from .serializers import (
    WalletSerializer, 
    WalletTransactionSerializer,
    WalletTopupSerializer
)
from .services import WalletService
from drf_spectacular.utils import extend_schema, OpenApiParameter


class WalletDetailView(generics.RetrieveAPIView):
    """
    Get current user's wallet information
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return WalletService.get_or_create_wallet(self.request.user)


class WalletTransactionListView(generics.ListAPIView):
    """
    Get current user's wallet transaction history
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='admin_topup',
                description='Filter by admin topup transactions (true=only topups, false=exclude topups)',
                required=False,
                type=bool
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        wallet = WalletService.get_or_create_wallet(self.request.user)
        queryset = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        # Filter by admin_topup parameter
        admin_topup = self.request.query_params.get('admin_topup')
        if admin_topup is not None:
            if admin_topup.lower() == 'true':
                # Only admin topup transactions
                queryset = queryset.filter(kind=WalletTransaction.Kind.ADMIN_TOPUP)
            elif admin_topup.lower() == 'false':
                # Exclude admin topup transactions
                queryset = queryset.exclude(kind=WalletTransaction.Kind.ADMIN_TOPUP)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def wallet_topup(request, user_id=None):
    """
    Top up wallet balance (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Only admin users can top up wallets'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = WalletTopupSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Admin top-up')
        target_user_id = user_id or serializer.validated_data.get('user_id')
        
        try:
            if target_user_id:
                from users.models import User
                target_user = User.objects.get(id=target_user_id)
            else:
                target_user = request.user
            
            wallet = WalletService.get_or_create_wallet(target_user)
            transaction = WalletService.process_topup(wallet, amount, description)
            
            response_data = {
                'message': 'Wallet topped up successfully',
                'user': target_user.username,
                'transaction': WalletTransactionSerializer(transaction).data,
                'new_balance': wallet.balance
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
