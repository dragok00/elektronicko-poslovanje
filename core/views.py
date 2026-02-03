from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .ai_logic import get_local_recommendations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

@api_view(['POST'])
@permission_classes([AllowAny])
def recommend_gifts(request):
    from .ai_logic import get_local_recommendations
    
    user_input = {
        'interests': request.data.get('interests', ''),
        'occasion': request.data.get('occasion', ''),
        'budget': float(request.data.get('budget', 1000)),
        'relationship': request.data.get('relationship', '')
    }
    
    recommended_products = get_local_recommendations(user_input)
    serializer = ProductSerializer(recommended_products, many=True)
    return Response(serializer.data)

from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def get_similar_products(request, product_id):
    try:
        source_product = Product.objects.get(id=product_id)
        
        mock_prefs = {
            'interests': source_product.interests,
            'occasion': source_product.occasion,
            'budget': float(source_product.price) * 1.3,
            'relationship': ''
        }
        similar = get_local_recommendations(mock_prefs).exclude(id=source_product.id)[:4]
        
        if not similar.exists():
            similar = Product.objects.filter(
                category=source_product.category
            ).exclude(id=source_product.id).order_by('?')[:4]
            
        if not similar.exists():
            similar = Product.objects.exclude(id=source_product.id).order_by('?')[:4]

        serializer = ProductSerializer(similar, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response([], status=404)
    

@api_view(['GET'])
def get_similar_products(request, pk):
    try:
        all_products = list(Product.objects.all())
        current_product = Product.objects.get(pk=pk)
        
        if len(all_products) < 2:
            return Response([])

        descriptions = [
            f"{p.name} {p.category} {p.description}" for p in all_products
        ]
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(descriptions)
        

        current_idx = all_products.index(current_product)
        cosine_sim = cosine_similarity(tfidf_matrix[current_idx], tfidf_matrix).flatten()
        
        similar_indices = cosine_sim.argsort()[-4:-1][::-1] 

        similar_products = [all_products[i] for i in similar_indices]
        
        serializer = ProductSerializer(similar_products, many=True)
        
        return Response(serializer.data)

    except Product.DoesNotExist:
        return Response({"error": "Proizvod nije pronađen"}, status=404)
    except Exception as e:
        print(f"AI Greška: {e}")
        return Response([])