# here we create the main logic for the API calls
import requests
import logging
from django.conf import settings
from .models import ShirtigoOrder, ShirtigoAPILog
# added for test
import json

logger = logging.getLogger(__name__)

class ShirtigoAPI:
    """
    Class to handle Api calls to Shirtigo.
    This class is responsible for creating, and monitorating orders.
    """
    def __init__(self):
        self.base_url = settings.SHIRTIGO_API_BASE_URL
        self.token = settings.SHIRTIGO_API_TOKEN
        self.headers = {
            'User-Agent': 'Shirtigo Cockpit Python REST API Client',
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, data=None, shirtigo_order=None):
        url = f'{self.base_url}{endpoint}'
        logger.info(f'Request URL: {url}')
        logger.info(f'Request Data: {json.dumps(data, indent=2)}')

        try:
            if method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'GET':
                response = requests.get(url, headers=self.headers)
            else:
                raise ValueError(f'Unsupported method: {method}')

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f'Errore API Shirtigo: {str(e)}')
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    logger.error(f'Error: {json.dumps(error_details, indent=2)}')
                except ValueError:
                    logger.error(f'Error: {e.response.text}')
            raise

    def create_order(self, shirtigo_order):
        """
        Create an order on Shirtigo with the details of the App order
        """
        order = shirtigo_order.order
        country_code = str(order.country).upper()
        
        # Customer and Shipping address detail
        order_data = {
            "delivery": {
                "type": "delivery",
                "firstname": order.full_name.split(' ')[0] if ' ' in order.full_name else order.full_name,
                "lastname": ' '.join(order.full_name.split(' ')[1:]) if ' ' in order.full_name else "",
                "street": order.street_address1,
                "postcode": order.postcode,
                "city": order.town_or_city,
                "country": str(order.country).upper(),
                "email": order.email_address
            },
            "products": []
        }

        # Add care of address if available
        if order.street_address2:
            order_data["delivery"]["care_of"] = order.street_address2
        
        # add phone number if available
        if order.phone_number:
            order_data["delivery"]["phone"] = order.phone_number
        
        # Add products to the order
        for item in order.items.all():
            # Verify that all necessary IDs are available
            if not hasattr(item.product, 'shirtigo_id') or not item.product.shirtigo_id:
                logger.warning(f"Product {item.product.id} without shirtigo_id")
                continue
                
            if not item.color or not hasattr(item.color, 'shirtigo_color_id') or not item.color.shirtigo_color_id:
                logger.warning(f"Missing color or without shirtigo_color_id for item {item.id}")
                continue

            if not item.size or not hasattr(item.size, 'shirtigo_size_id') or not item.size.shirtigo_size_id:
                logger.warning(f"Missing size or without shirtigo_size_id for item {item.id}")
                continue
            
            # Add the product to the order data
            order_data["products"].append({
                "productId": item.product.shirtigo_id,
                "colorId": item.color.shirtigo_color_id,
                "sizeId": item.size.shirtigo_size_id,
                "amount": item.quantity
            })

        # Verify if there are products to order
        if not order_data["products"]:
            error_msg = "No valid products to order to Shirtigo"
            logger.error(error_msg)
            shirtigo_order.status = 'failed'
            shirtigo_order.status_message = error_msg
            shirtigo_order.save()
            raise ValueError(error_msg)
        
        # Send the request to Shirtigo
        try:
            response = self._make_request('POST', '/orders', data=order_data, shirtigo_order=shirtigo_order)
            
            if response.get('reference'):
                shirtigo_order.shirtigo_order_id = response['reference']
                shirtigo_order.status = 'created'
                shirtigo_order.status_message = 'Order created in Shirtigo'
                shirtigo_order.save()
                # Update the status of the main order
                order.status = 'processing'
                order.paid = True            
                order.save()
            else:
                raise ValueError("Invalid response from Shirtigo")
        except Exception as e:
            logger.error(f"Error during order creation in Shirtigo: {str(e)}", exc_info=True)
            # Update the order status to reflect the error
            order.status = 'pending'
            order.paid = False
            order.save()
        return response