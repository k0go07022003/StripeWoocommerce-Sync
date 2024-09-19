import stripe
import logging

logger = logging.getLogger(__name__)

class StripeHandler:
    def __init__(self, api_key, webhook_secret):
        self.stripe = stripe
        self.stripe.api_key = api_key
        self.webhook_secret = webhook_secret

    def construct_event(self, payload, sig_header):
        return self.stripe.Webhook.construct_event(
            payload, sig_header, self.webhook_secret
        )

    def process_checkout_session(self, session):
        logger.info(f"Przetwarzanie sesji checkout: {session['id']}")
        line_items = self.stripe.checkout.Session.list_line_items(session['id'], limit=5)
        logger.info(f"Pobrano {len(line_items.data)} line items")
        return line_items.data
    
    def get_all_products(self):
        try:
            products = self.stripe.Product.list(limit=100, active=True)
            return products.data
        except Exception as e:
            logger.error(f"Błąd podczas pobierania produktów ze Stripe: {str(e)}")
            return []