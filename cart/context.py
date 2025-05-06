from django.shortcuts import get_object_or_404
from products.models import Product, Color, Size, ProductImage
from .models import Cart, CartItem

def cart_contents(request):
    """
    Make cart contents available across all templates.
    """
    cart_items = []
    cart_total = 0
    
    if request.user.is_authenticated:
        # Handle authenticated users with database Cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = []
            
            # Get items from the database
            db_items = CartItem.objects.filter(cart=cart).select_related('product', 'color', 'size')
            
            for item in db_items:
                # Get product image matching color
                image = item.product.images.filter(color=item.color).first()
                image_url = image.small_image if image else ''
                
                # Calculate price per item
                price = item.quantity * item.product.price
                cart_total += price
                
                # Add item to list
                cart_items.append({
                    'id': item.id,
                    'product': item.product,
                    'quantity': item.quantity,
                    'color': item.color,
                    'size': item.size,
                    'price': price,
                    'image_url': image_url,
                })
        except Cart.DoesNotExist:
            # User has no cart yet
            pass
    else:
        # Handle non-authenticated users with session Cart
        cart = request.session.get('cart', {})
        
        for key, cart_item in cart.items():
            product_id, color_id, size_id = key.split(':')
            
            try:
                product = Product.objects.get(id=product_id)
                color = Color.objects.get(id=color_id) if color_id else None
                size = Size.objects.get(id=size_id) if size_id else None
                quantity = cart_item.get('quantity', 1)
                
                # Get product image matching color
                image = product.images.filter(color=color).first()
                image_url = image.small_image if image else ''
                
                # Calculate price
                price = quantity * product.price
                cart_total += price
                
                # Add item to list
                cart_items.append({
                    'key': key,
                    'product': product,
                    'quantity': quantity,
                    'color': color,
                    'size': size,
                    'price': price,
                    'image_url': image_url,
                })
            except (Product.DoesNotExist, Color.DoesNotExist, Size.DoesNotExist):
                # Handle invalid items in cart
                pass
    
    cart_count = len(cart_items)
    
    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }