from django.contrib import admin
from .models import Category, Color, Product, ProductImage

# Register your models here.
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Product)
admin.site.register(ProductImage)