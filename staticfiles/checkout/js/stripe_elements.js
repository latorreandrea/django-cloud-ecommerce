/**
 * Stripe Elements integration for Django Cloud Ecommerce
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get Stripe public key
    const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);
    
    // Initialize Stripe
    const stripe = Stripe(stripePublicKey);
    
    // Custom styling for Stripe Elements
    const elements = stripe.elements({
        fonts: [
            {
                cssSrc: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap',
            },
        ],
        locale: 'auto'
    });
    
    const style = {
        base: {
            fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            fontSize: '16px',
            fontSmoothing: 'antialiased',
            lineHeight: '1.4',
            color: '#32325d',
            '::placeholder': {
                color: '#aab7c4',
            },
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };
    
    // Create the card element
    const card = elements.create('card', {
        style: style,
        hidePostalCode: true
    });
    
    // Mount the card element to the DOM
    card.mount('#card-element');
    
    // Handle validation errors
    card.addEventListener('change', function(event) {
        const errorDiv = document.getElementById('card-errors');
        
        if (event.error) {
            errorDiv.textContent = event.error.message;
        } else {
            errorDiv.textContent = '';
        }
        
        // Update the card visual representation based on the input
        updateCardDisplay(event);
    });
    
    // Function to update the card display based on Stripe card input
    function updateCardDisplay(event) {
        // Card display elements
        const cardDisplayNumber = document.getElementById('card-display-number');
        const cardDisplayName = document.getElementById('card-display-name');
        const cardDisplayExpiry = document.getElementById('card-display-expiry');
        const cardDisplayCvc = document.getElementById('card-display-cvc');
        const cardFront = document.querySelector('.jp-card-front');
        const cardBack = document.querySelector('.jp-card-back');
        
        // Get card details from the event
        const brand = event.brand;
        const complete = event.complete;
        const empty = event.empty;
        
        // Update card number display
        if (!empty) {
            if (event.elementType === 'cardNumber' || !event.elementType) {
                const lastFourDigits = event.value && event.value.card ? event.value.card.last4 : '';
                if (lastFourDigits) {
                    cardDisplayNumber.textContent = '•••• •••• •••• ' + lastFourDigits;
                }
            }
            
            // Update card brand styling
            const cardContainer = document.querySelector('.jp-card');
            if (cardContainer) {
                // Remove all brand classes
                cardContainer.classList.remove(
                    'jp-card-visa', 
                    'jp-card-mastercard', 
                    'jp-card-amex', 
                    'jp-card-discover'
                );
                
                // Add appropriate brand class
                if (brand === 'visa') {
                    cardContainer.classList.add('jp-card-visa');
                } else if (brand === 'mastercard') {
                    cardContainer.classList.add('jp-card-mastercard');
                } else if (brand === 'amex') {
                    cardContainer.classList.add('jp-card-amex');
                } else if (brand === 'discover') {
                    cardContainer.classList.add('jp-card-discover');
                }
            }
            
            // Handle focus state for CVC
            if (event.elementType === 'cardCvc') {
                // Show the back of the card when focusing on CVC
                cardFront.style.display = 'none';
                cardBack.style.display = 'block';
                
                // Simulate dots for security code
                cardDisplayCvc.textContent = '•••';
            } else {
                // Show front of card for all other fields
                cardFront.style.display = 'block';
                cardBack.style.display = 'none';
            }
            
            // Handle name - We'll use the shipping name as cardholder name
            const shippingName = document.getElementById('id_full_name');
            if (shippingName && shippingName.value) {
                cardDisplayName.textContent = shippingName.value;
            } else {
                cardDisplayName.textContent = 'Your Name';
            }
        }
    }
    
    // Watch for name changes to update the card
    const nameInput = document.getElementById('id_full_name');
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            const cardDisplayName = document.getElementById('card-display-name');
            cardDisplayName.textContent = this.value || 'Your Name';
        });
    }
    
    // Handle form submission
    const form = document.getElementById('checkout-form');
    const submitButton = document.getElementById('submit');
    
    form.addEventListener('submit', async function(ev) {
        ev.preventDefault();
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        // Create loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.style.position = 'fixed';
        loadingOverlay.style.top = '0';
        loadingOverlay.style.left = '0';
        loadingOverlay.style.width = '100%';
        loadingOverlay.style.height = '100%';
        loadingOverlay.style.backgroundColor = 'rgba(255,255,255,0.7)';
        loadingOverlay.style.zIndex = '9999';
        loadingOverlay.style.display = 'flex';
        loadingOverlay.style.justifyContent = 'center';
        loadingOverlay.style.alignItems = 'center';
        loadingOverlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Processing payment...</span></div>';
        document.body.appendChild(loadingOverlay);
        
        // Clear any previous errors
        document.getElementById('card-errors').textContent = '';
        
        // Process the payment with Stripe
        try {
            // Prepare form data
            const formData = new FormData(form);
            
            // Get CSRF token
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // First create the order on the backend
            const response = await fetch('/checkout/create-order/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                if (data.errors) {
                    let errorMessage = 'Please check the form for errors.';
                    document.getElementById('card-errors').textContent = errorMessage;
                } else if (data.error) {
                    document.getElementById('card-errors').textContent = data.error;
                }
                submitButton.disabled = false;
                submitButton.innerHTML = '<span class="d-flex align-items-center justify-content-center"><span class="me-2">Pay now</span><i class="fas fa-lock"></i></span>';
                document.body.removeChild(loadingOverlay);
                return;
            }
            
            // Generate idempotency key
            const requestId = `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
            
            // Process payment with Stripe
            const result = await stripe.confirmCardPayment(data.client_secret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById('id_full_name').value,
                        email: document.getElementById('id_email_address').value,
                        address: {
                            line1: document.getElementById('id_street_address1').value,
                            line2: document.getElementById('id_street_address2').value || '',
                            city: document.getElementById('id_town_or_city').value,
                            state: document.getElementById('id_county').value || '',
                            postal_code: document.getElementById('id_postcode').value,
                            country: document.getElementById('id_country').value
                        }
                    }
                },
                shipping: {
                    name: document.getElementById('id_full_name').value,
                    address: {
                        line1: document.getElementById('id_street_address1').value,
                        line2: document.getElementById('id_street_address2').value || '',
                        city: document.getElementById('id_town_or_city').value,
                        state: document.getElementById('id_county').value || '',
                        postal_code: document.getElementById('id_postcode').value,
                        country: document.getElementById('id_country').value
                    }
                }
            }, {
                idempotencyKey: requestId
            });
            
            // Handle payment result
            if (result.error) {
                let errorMessage = result.error.message;
                
                if (result.error.type === 'card_error') {
                    errorMessage = `Card issue: ${result.error.message}`;
                } else if (result.error.type === 'validation_error') {
                    errorMessage = `Validation issue: ${result.error.message}`;
                }
                
                document.getElementById('card-errors').textContent = errorMessage;
                submitButton.disabled = false;
                submitButton.innerHTML = '<span class="d-flex align-items-center justify-content-center"><span class="me-2">Pay now</span><i class="fas fa-lock"></i></span>';
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    // Add payment intent ID to form and redirect
                    const paymentIntentInput = document.createElement('input');
                    paymentIntentInput.type = 'hidden';
                    paymentIntentInput.name = 'payment_intent_id';
                    paymentIntentInput.value = result.paymentIntent.id;
                    form.appendChild(paymentIntentInput);
                    
                    // Redirect to success page
                    window.location.href = `/checkout/success/?order_id=${data.order_id}&payment_confirmed=true`;
                } else if (result.paymentIntent.status === 'requires_action') {
                    // Handle 3D Secure
                    const { error, paymentIntent } = await stripe.confirmCardPayment(data.client_secret);
                    
                    if (error) {
                        document.getElementById('card-errors').textContent = 'Authentication failed.';
                        submitButton.disabled = false;
                        submitButton.innerHTML = '<span class="d-flex align-items-center justify-content-center"><span class="me-2">Pay now</span><i class="fas fa-lock"></i></span>';
                    } else if (paymentIntent.status === 'succeeded') {
                        // Add payment intent ID to form
                        const paymentIntentInput = document.createElement('input');
                        paymentIntentInput.type = 'hidden';
                        paymentIntentInput.name = 'payment_intent_id';
                        paymentIntentInput.value = paymentIntent.id;
                        form.appendChild(paymentIntentInput);
                        
                        // Redirect to success page
                        window.location.href = `/checkout/success/?order_id=${data.order_id}&payment_confirmed=true`;
                    }
                }
            }
        } catch (error) {
            console.error('Payment Error:', error);
            
            let errorMessage = 'An unexpected error occurred. Please try again.';
            
            if (!navigator.onLine) {
                errorMessage = 'You seem to be offline. Please check your internet connection.';
            }
            
            document.getElementById('card-errors').textContent = errorMessage;
            submitButton.disabled = false;
            submitButton.innerHTML = '<span class="d-flex align-items-center justify-content-center"><span class="me-2">Pay now</span><i class="fas fa-lock"></i></span>';
        } finally {
            // Remove loading overlay
            if (document.body.contains(loadingOverlay)) {
                document.body.removeChild(loadingOverlay);
            }
        }
    });
});