from django.urls import path
from . import views, admin_views



urlpatterns = [
    path('', views.ProductListView.as_view(), name='products_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    # ADMIN URLS
    path('admin/update-products/', admin_views.update_products, name='update_products'),
]
