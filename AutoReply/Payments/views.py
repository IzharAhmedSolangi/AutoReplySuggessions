from django.http import JsonResponse
import stripe
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCaptureRequest,OrdersCreateRequest

from . import config

stripe.api_key = config.PAYMENT_GATEWAY_CONFIG['stripe']['api_key']
paypal_config = config.PAYMENT_GATEWAY_CONFIG['paypal']

def create_payment(request):
    payment_gateway = request.POST.get('payment_gateway')
    amount = request.POST.get('amount')
    # Validate payment gateway and amount

    if payment_gateway == 'stripe':
        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=['card']
        )

        # Return the client secret for the payment intent
        return JsonResponse({'status': 'success', 'client_secret': intent.client_secret})

    elif payment_gateway == 'paypal':
        # Create a PayPal order
        environment = SandboxEnvironment(client_id=paypal_config['client_id'], client_secret=paypal_config['client_secret'])
        client = PayPalHttpClient(environment)
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": amount
                }
            }]
        })
        response = client.execute(request)
        order_id = response.result.id

        # Return the PayPal order ID
        return JsonResponse({'status': 'success', 'order_id': order_id})

    else:
        # Invalid payment gateway, handle the response
        return JsonResponse({'status': 'error', 'message': 'Invalid payment gateway'})
