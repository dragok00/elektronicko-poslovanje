from django.contrib import admin
from .models import Product, Recommendation, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'occasion')
    search_fields = ('name', 'description', 'interests')
    list_filter = ('category', 'occasion')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')


admin.site.register(Recommendation)
