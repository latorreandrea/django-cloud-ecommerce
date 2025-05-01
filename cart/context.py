from django.shortcuts import get_object_or_404
from products.models import Product, Color, Size, ProductImage

def cart_contents(request):
    """
    Returns the contents of the cart as a dictionary.
    Includes product, color, size, cart_count (number of products), and cart_total (sum of prices).
    """
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for key, item in cart.items():
        if not isinstance(item, dict):
            continue
        product = get_object_or_404(Product, pk=int(item['product']))
        color = None
        size = None
        image_url = None
        if item.get('color'):
            color = Color.objects.filter(id=item['color']).first()
            image = ProductImage.objects.filter(product=product, color=color).first()
            if image:
                image_url = image.small_image
        if item.get('size'):
            size = Size.objects.filter(id=item['size']).first()
        price = product.price
        cart_items.append({
            'key': key,
            'product': product,
            'color': color,
            'size': size,
            'price': price,
            'image_url': image_url,
        })
        cart_total += price

    cart_count = len(cart_items)

    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': cart_count,
    }
    