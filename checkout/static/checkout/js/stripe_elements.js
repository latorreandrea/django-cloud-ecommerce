/**
 * Stripe Elements integration for Django Cloud Ecommerce
 * 
 * This file handles the Stripe payment process:
 * 1. Initialize Stripe Elements
 * 2. Create an order on the server
 * 3. Process payment with Stripe
 * 4. Handle successful payments or errors
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get the Stripe public key from the template
    const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);

    // Initialize Stripe with Elements
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    
    // Create and mount the card element
    const card = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                fontFamily: '"Open Sans", sans-serif',
                color: '#32325d',
                '::placeholder': {
                    color: '#aab7c4',
                },
            },
            invalid: {
                color: '#dc3545',
                iconColor: '#dc3545'
            }
        }
    });
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element
    card.on('change', function(event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.textContent = event.error.message;
        } else {
            errorDiv.textContent = '';
        }
    });

    // Get reference to the payment form
    const form = document.getElementById('checkout-form');
    const submitButton = document.getElementById('submit');
    
    // Handle form submission
    form.addEventListener('submit', async function(ev) {
        ev.preventDefault();
        
        // Disable submit button to prevent multiple submissions
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        // Create loading overlay to prevent user interaction during processing
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
        
        // Clear any previous error messages
        document.getElementById('card-errors').textContent = '';
        
        // Set up a timeout to prevent indefinite waiting
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), 30000)
        );
        
        try {
            // Prepare the form data
            const formData = new FormData(form);
            
            // Get CSRF token from the form
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // First create the order on the backend
            const response = await Promise.race([
                fetch('/checkout/create-order/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: formData
                }),
                timeoutPromise
            ]);
            
            // Parse the JSON response
            const data = await response.json();
            
            if (!response.ok) {
                // Handle validation errors
                if (data.errors) {
                    let errorMessage = 'Please check the form for errors.';
                    document.getElementById('card-errors').textContent = errorMessage;
                } else if (data.error) {
                    document.getElementById('card-errors').textContent = data.error;
                }
                submitButton.disabled = false;
                submitButton.textContent = 'Pay now';
                document.body.removeChild(loadingOverlay);
                return;
            }
            
            // Generate a unique request ID for idempotency
            const requestId = `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
            
            // Now confirm the payment with Stripe using the client secret
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
                // Include shipping information for fraud prevention
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
                // Include idempotency key to prevent duplicate charges
                idempotencyKey: requestId
            });
            
            // Handle the payment result
            if (result.error) {
                // Format user-friendly error messages based on error type
                let errorMessage = result.error.message;
                
                if (result.error.type === 'card_error') {
                    errorMessage = `Card issue: ${result.error.message}`;
                } else if (result.error.type === 'validation_error') {
                    errorMessage = `Validation issue: ${result.error.message}`;
                }
                
                document.getElementById('card-errors').textContent = errorMessage;
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    // Store payment intent ID in local storage for reference
                    localStorage.setItem('lastPaymentIntent', result.paymentIntent.id);
                    
                    // Add payment intent ID to form and redirect
                    const paymentIntentInput = document.createElement('input');
                    paymentIntentInput.type = 'hidden';
                    paymentIntentInput.name = 'payment_intent_id';
                    paymentIntentInput.value = result.paymentIntent.id;
                    form.appendChild(paymentIntentInput);
                    
                    // Redirect to success page
                    window.location.href = `/checkout/success/?order_id=${data.order_id}&payment_confirmed=true`;
                } else if (result.paymentIntent.status === 'requires_action') {
                    // Handle 3D Secure authentication if required
                    const { error, paymentIntent } = await stripe.confirmCardPayment(data.client_secret);
                    
                    if (error) {
                        document.getElementById('card-errors').textContent = 'Authentication failed.';
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
            // Handle network errors and other exceptions
            console.error('Payment Error:', error);
            
            // Provide user-friendly error messages
            let errorMessage = 'An unexpected error occurred. Please try again.';
            
            if (error.message === 'Request timeout') {
                errorMessage = 'The payment is taking too long to process. Please try again.';
            } else if (!navigator.onLine) {
                errorMessage = 'You seem to be offline. Please check your internet connection.';
            }
            
            document.getElementById('card-errors').textContent = errorMessage;
        } finally {
            // Always clean up the UI regardless of outcome
            submitButton.disabled = false;
            submitButton.textContent = 'Pay now';
            
            // Remove loading overlay
            if (document.body.contains(loadingOverlay)) {
                document.body.removeChild(loadingOverlay);
            }
        }
    });
});