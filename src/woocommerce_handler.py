from woocommerce import API
import logging
from .models import Product
import datetime


logger = logging.getLogger(__name__)

class WooCommerceHandler:
    def __init__(self, woo_config):
        self.wcapi = API(
            url=woo_config['url'],
            consumer_key=woo_config['consumer_key'],
            consumer_secret=woo_config['consumer_secret'],
            version="wc/v3",
            timeout=30
        )
        logger.info(f"WooCommerceHandler zainicjalizowany z konfiguracją: {woo_config}")

    def get_all_products(self):
            logger.info("Pobieranie wszystkich produktów z WooCommerce")
            products = []
            page = 1
            per_page = 100

            while True:
                try:
                    response = self.wcapi.get("products", params={
                        "page": page,
                        "per_page": per_page,
                        "status": "publish"  # Pobieramy tylko opublikowane produkty
                    })
                    
                    if response.status_code != 200:
                        logger.error(f"Błąd podczas pobierania produktów. Status: {response.status_code}, Treść: {response.text}")
                        break

                    new_products = response.json()
                    if not new_products:
                        break

                    products.extend(new_products)
                    logger.info(f"Pobrano {len(new_products)} produktów ze strony {page}")
                    
                    page += 1
                except Exception as e:
                    logger.error(f"Wystąpił błąd podczas pobierania produktów: {str(e)}")
                    break

            logger.info(f"Łącznie pobrano {len(products)} produktów")
            return products

    def create_order(self, stripe_session, line_items):
        logger.info(f"Rozpoczęcie tworzenia zamówienia dla sesji: {stripe_session['id']}")

        # Sprawdź istniejące zamówienia z ostatnich 7 dni
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        page = 1
        per_page = 100

        while True:
            try:
                orders = self.wcapi.get("orders", params={
                    "after": seven_days_ago.isoformat(),
                    "page": page,
                    "per_page": per_page
                }).json()

                if not orders:
                    break

                for order in orders:
                    if "meta_data" in order:
                        for meta in order['meta_data']:
                            if meta['key'] == "stripe_session_id" and meta['value'] == stripe_session['id']:
                                logger.info(f"Zamówienie dla sesji {stripe_session['id']} już istnieje: {order['id']}")
                                return order

                page += 1
            except Exception as e:
                logger.error(f"Błąd podczas pobierania zamówień: {str(e)}")
                break

        logger.info("Tworzenie nowego zamówienia")
        try:
            customer = self.get_or_create_customer(stripe_session['customer_details'])
            logger.info(f"Utworzono/znaleziono klienta: {customer['id']}")

            logger.info(f"Pobrano line items ze Stripe: {line_items}")

            woo_line_items = self.prepare_line_items(line_items)
            logger.info(f"Przygotowane line items dla WooCommerce: {woo_line_items}")

            order_data = {
                "payment_method": "stripe",
                "payment_method_title": "Stripe",
                "set_paid": True,
                "status": "completed",
                "customer_id": customer['id'],
                "billing": {
                    "email": stripe_session['customer_details']['email'],
                    "first_name": stripe_session['customer_details']['name']
                },
                "line_items": woo_line_items,
                "meta_data": [
                    {"key": "stripe_session_id", "value": stripe_session['id']},
                    {"key": "stripe_payment_intent", "value": stripe_session['payment_intent']}
                ]
            }

            logger.info(f"Dane zamówienia do wysłania: {order_data}")
            response = self.wcapi.post("orders", order_data)
            if response.status_code != 201:
                logger.error(f"Błąd przy tworzeniu zamówienia. Status: {response.status_code}, Treść: {response.text}")
                raise Exception(f"Błąd przy tworzeniu zamówienia: {response.text}")

            new_order = response.json()
            logger.info(f"Utworzono nowe zamówienie: {new_order['id']}")
            return new_order
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia zamówienia: {str(e)}")
            raise

    def get_or_create_customer(self, customer_details):
        customers = self.wcapi.get("customers", params={"email": customer_details['email']}).json()
        if customers:
            return customers[0]
        else:
            customer_data = {
                "email": customer_details['email'],
                "first_name": customer_details['name']
            }
            response = self.wcapi.post("customers", customer_data)
            return response.json()

    def prepare_line_items(self, stripe_line_items):
        woo_line_items = []
        for item in stripe_line_items:
            product = Product.query.filter_by(stripe_id=item['price']['product']).first()
            if product:
                woo_product_ids = product.get_woo_product_ids()
                for woo_product_id in woo_product_ids:
                    woo_line_items.append({
                        "product_id": woo_product_id,
                        "quantity": item['quantity'],
                        "total": str(item['amount_total'] / 100 / len(woo_product_ids))
                    })
            else:
                logger.error(f"Nie znaleziono mapowania dla produktu Stripe: {item['price']['product']}")
        return woo_line_items