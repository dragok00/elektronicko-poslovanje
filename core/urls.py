from django.urls import path
from .views import ProductListView, register_user, create_order, get_user_orders

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('register/', register_user, name='register'),
    path('orders/create/', create_order, name='create-order'),
    path('orders/my-orders/', get_user_orders, name='user-orders'),
]