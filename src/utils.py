from .models import Config

def load_config():
    config = {
        'woocommerce': {
            'url': Config.get_value('woocommerce_url'),
            'consumer_key': Config.get_value('woocommerce_consumer_key'),
            'consumer_secret': Config.get_value('woocommerce_consumer_secret'),
        },
        'stripe': {
            'api_key': Config.get_value('stripe_api_key'),
            'webhook_secret': Config.get_value('stripe_webhook_secret'),
        }
    }
    return config

def save_config(new_config):
    Config.set_value('woocommerce_url', new_config['woocommerce']['url'])
    Config.set_value('woocommerce_consumer_key', new_config['woocommerce']['consumer_key'])
    Config.set_value('woocommerce_consumer_secret', new_config['woocommerce']['consumer_secret'])
    Config.set_value('stripe_api_key', new_config['stripe']['api_key'])
    Config.set_value('stripe_webhook_secret', new_config['stripe']['webhook_secret'])