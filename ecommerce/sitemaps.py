# ecommerce/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category
from home.views import index, about, our_mission, contact, support, faq

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return f'/products/{obj.id}/'

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Category.objects.all()
    
    def location(self, obj):
        return f'/products/?category={obj.friendly_name}'

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            # Home and info pages
            'home', 'about', 'our_mission', 'contact', 'support', 'faq',
            'privacy_policy', 'terms_of_service', 'shipping_returns',
            
            # Product pages
            'products_list',
            
            # Shopping pages
            'cart', 'wishlist', 'checkout',
            
            # Authentication pages (public)
            'account_login', 'account_signup',
        ]

    def location(self, item):
        return reverse(item)

class NewsletterSitemap(Sitemap):
    priority = 0.3
    changefreq = 'yearly'
    
    def items(self):
        return ['newsletter:subscribe']
    
    def location(self, item):
        return reverse(item)