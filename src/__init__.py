from flask import Flask, request, jsonify
from .stripe_handler import StripeHandler
from .woocommerce_handler import WooCommerceHandler
from .utils import load_config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging
from .extensions import db, login_manager
import yaml

# Inicjalizacja obiektów


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Ładowanie konfiguracji bazy danych z pliku YAML
    with open('src/config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Konfiguracja aplikacji
    app.config['SQLALCHEMY_DATABASE_URI'] = config['sqlalchemy']['database_url']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config['sqlalchemy']['secret_key']
    
    # Inicjalizacja bazy danych
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Inicjalizacja pustych wartości dla WooCommerce i Stripe
        from .models import Config
        for key in ['woocommerce_url', 'woocommerce_consumer_key', 'woocommerce_consumer_secret', 'stripe_api_key', 'stripe_webhook_secret']:
            if not Config.get_value(key):
                Config.set_value(key, '')

        # Ładowanie konfiguracji
        from .utils import load_config
        config.update(load_config())
    
    # Inicjalizacja handlerów tylko jeśli są skonfigurowane
    if all(config['woocommerce'].values()):
        app.config['WOOCOMMERCE_CONFIG'] = config['woocommerce']
        woocommerce_handler = WooCommerceHandler(config['woocommerce'])
    else:
        woocommerce_handler = None

    if all(config['stripe'].values()):
        app.config['STRIPE_API_KEY'] = config['stripe']['api_key']
        app.config['STRIPE_WEBHOOK_SECRET'] = config['stripe']['webhook_secret']
        stripe_handler = StripeHandler(config['stripe']['api_key'], config['stripe']['webhook_secret'])
    else:
        stripe_handler = None

    # Inicjalizacja login managera
    login_manager.init_app(app)

    # Inicjalizacja blueprintów dla admina
    from .admin_views import admin_bp
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    @app.route('/webhook', methods=['POST'])
    def stripe_webhook():
        if not stripe_handler:
            return jsonify({'error': 'Stripe not configured'}), 500
        logger.info("Otrzymano żądanie webhooka")
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')

        logger.info(f"Otrzymano payload o długości: {len(payload)} bajtów")
        logger.info(f"Signature Header: {sig_header}")

        try:
            event = stripe_handler.construct_event(payload, sig_header)
            logger.info(f"Poprawnie skonstruowano event typu: {event['type']}")
        except ValueError as e:
            logger.error(f"Błąd weryfikacji webhooka: {str(e)}")
            return jsonify({'error': str(e)}), 400

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            logger.info(f"Otrzymano sesję checkout o ID: {session['id']}")
            try:
                logger.info("Próba utworzenia zamówienia w WooCommerce")
                line_items = stripe_handler.process_checkout_session(session)
                new_order = woocommerce_handler.create_order(session, line_items)
                logger.info(f"Przetworzono zamówienie: {new_order['id']}")
                return jsonify(success=True), 200
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania zamówienia: {str(e)}", exc_info=True)
                return jsonify({'error': 'Nie udało się przetworzyć zamówienia'}), 500
        else:
            logger.info(f"Otrzymano event innego typu niż checkout.session.completed: {event['type']}")

        return jsonify(success=True), 200

    @app.route('/')
    def home():
        return "Aplikacja działa!"

    # Dodaj tę linię, aby wyświetlić wszystkie zarejestrowane trasy
    logger.info(f"Zarejestrowane trasy: {app.url_map}")

    return app