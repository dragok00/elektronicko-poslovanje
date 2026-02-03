from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Molimo unesite sve podatke'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Korisničko ime je zauzeto'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'message': 'Korisnik uspješno kreiran'}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    Order.objects.create(
        user=request.user,
        items=request.data.get('items'),
        total_price=request.data.get('total')
    )
    return Response({"message": "Narudžba uspješna!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    orders = Order.objects.filter(user=request.user).values()
    return Response(orders)