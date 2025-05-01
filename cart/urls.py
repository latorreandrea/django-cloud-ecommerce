from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
]