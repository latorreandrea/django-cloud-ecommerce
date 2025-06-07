import os
import requests
import django
import logging
# model imports
from products.models import Category, Color, Product, ProductImage, Size


# logging configuration
logger = logging.getLogger(__name__)

# Setup API
API_KEY = os.environ.get('SHIRTIGO_API_TOKEN')
BASE_URL = "https://cockpit.shirtigo.com/api/"
PRODUCTS_URL = "products?include=projectProductColors"
headers = {
    'User-Agent': 'Shirtigo Cockpit Python REST API Client',
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def get_products():
    """
    Fetches the list of products from the Shirtigo API.
    """
    url = BASE_URL + PRODUCTS_URL
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def get_all_categorys(json_data):
    """
    Extracts all categories from the product data.
    """
    categorys = [item.get('name') for item in json_data['data'] if 'name' in item]
    return list(set(categorys))


def get_all_colors(json_data):
    """
    Extracts all colors from the product data.
    """
    color_dict = {}
    for item in json_data['data']:
        for image in item.get('images', []):
            color = image.get('color')
            color_id = image.get('color_id')
            if color and color_id:
                color_dict[color] = color_id
    return color_dict


def get_all_sizes(json_data):
    """
    Estrae tutte le taglie (sizes) dai dati del prodotto.
    """
    size_dict = {}
    for item in json_data['data']:
        if 'projectProductColors' in item and 'data' in item['projectProductColors']:
            for color in item['projectProductColors']['data']:
                if 'sizes' in color:
                    for size in color['sizes']:
                        size_name = size.get('size')
                        size_id = size.get('id')
                        if size_name and size_id:
                            size_dict[size_name] = size_id
    return size_dict


def get_all_products(json_data):
    """
    Extracts all products from the product data including available sizes.
    """
    products = []
    for item in json_data['data']:
        # Calcola il prezzo arrotondando ESPLICITAMENTE a 2 decimali
        price_amount = float(item.get('price', {}).get('amount', 0))
        price_factor = float(item.get('price', {}).get('currency_factor', 1))
        price = round(price_amount / price_factor, 2)
        
        # Calcola il costo arrotondando ESPLICITAMENTE a 2 decimali
        cost_amount = float(item.get('shirtigo_price', {}).get('amount', 0))
        cost_factor = float(item.get('shirtigo_price', {}).get('currency_factor', 1))
        cost = round(cost_amount / cost_factor, 2)
        # Raccogli tutte le taglie disponibili per questo prodotto
        shirtigo_sizes = set()
        if 'projectProductColors' in item and 'data' in item['projectProductColors']:
            for color in item['projectProductColors']['data']:
                if 'sizes' in color:
                    for size in color['sizes']:
                        size_id = size.get('id')
                        if size_id:
                            shirtigo_sizes.add(size_id)

        
        
        product = {
            'name': item.get('project_name'),
            'shirtigo_id': item.get('id'),
            'category_name': item.get('name'),
            'description': item.get('description'),
            'price': price,  
            'cost': cost,  
            'shirtigo_colors': [image.get('color_id') for image in item.get('images', []) if image.get('color_id')],
            'shirtigo_sizes': list(shirtigo_sizes),  # Aggiungi le taglie disponibili
        }
        products.append(product)
    return products

def get_images(json_data):
    """
    Extracts all images from the product data.
    """
    images = []
    for item in json_data['data']:
        for image in item.get('images', []):
            img = {
                'product_shirtigo_id': item.get('id'),
                'shirtigo_color_id': image.get('color_id'),
                'small_image': image.get('urls').get('small'),
                'large_image': image.get('urls').get('large')
            }
            images.append(img)
    return images

def clear_products_tables():
    """
    Deletes all data from Category, Color, Product, and ProductImage tables.
    """
    from products.models import Category, Color, Product, ProductImage
    ProductImage.objects.all().delete()
    Product.objects.all().delete()
    Color.objects.all().delete()
    Category.objects.all().delete()
    print("All products tables have been cleared.")


def main():
    """
    Main function to create and populate tables
    in our database with the data 
    taken from the Shirtigo API
    """
    products_list = get_products()
    categories = get_all_categorys(products_list)
    colors = get_all_colors(products_list)
    sizes = get_all_sizes(products_list)
    products = get_all_products(products_list)
    images = get_images(products_list)
    
    # 1. Category
    category_objs = {}
    for cat_name in categories:
        obj, _ = Category.objects.get_or_create(name=cat_name)
        category_objs[cat_name] = obj

    # 2. Color
    color_objs = {}
    for color_name, color_id in colors.items():
        obj, _ = Color.objects.get_or_create(name=color_name, shirtigo_color_id=color_id)
        color_objs[color_id] = obj

    # 2.5 Size
    size_objs = {}
    for size_name, size_id in sizes.items():
        obj, _ = Size.objects.get_or_create(name=size_name, shirtigo_size_id=size_id)
        size_objs[size_id] = obj

    # 3. Product
    product_objs = {}
    for prod in products:
        cat_obj = category_objs.get(prod.get('category_name'))
        product, created = Product.objects.get_or_create(
            shirtigo_id=prod['shirtigo_id'],
            defaults={
                'name': prod['name'],                
                'category': cat_obj,
                'description': prod['description'],                
                'price': round(prod['price'], 2),
                'cost': round(prod['cost'], 2)
            }
        )
        if not created:
            # Update fields if already exists
            product.name = prod['name']
            product.category = cat_obj
            product.description = prod['description']
            product.price = round(prod['price'], 2)
            product.cost = round(prod['cost'], 2)
            product.save()
        # Set colors
        if prod['shirtigo_colors']:
            product.colors.set([color_objs[cid].id for cid in prod['shirtigo_colors'] if cid in color_objs])
        
        # Set sizes
        if prod['shirtigo_sizes']:
            product.sizes.set([size_objs[sid].id for sid in prod['shirtigo_sizes'] if sid in size_objs])
            
        product_objs[prod['shirtigo_id']] = product

    # 4. ProductImage
    for img in images:
        product = product_objs.get(img['product_shirtigo_id'])
        color = color_objs.get(img['shirtigo_color_id'])
        if product and color:
            ProductImage.objects.update_or_create(
                product=product,
                color=color,
                defaults={
                    'small_image': img['small_image'],
                    'large_image': img['large_image'],
                }
            )
    print("Database updated successfully!")
    # clear_products_tables()


if __name__ == "__main__":
    main()