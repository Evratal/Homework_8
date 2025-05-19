import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_product(name, description):
    return stripe.Product.create(name=name, description=description)

def create_stripe_price(amount, product_id, currency='rub'):
    return stripe.Price.create(
        unit_amount=int(amount * 100),  # Переводим в копейки
        currency=currency,
        product=product_id
    )

def create_stripe_session(price_id, success_url, cancel_url):
    return stripe.checkout.Session.create(
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )