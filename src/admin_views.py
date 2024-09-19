from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db
from .models import User, Product
from .forms import LoginForm, ProductForm
from .woocommerce_handler import WooCommerceHandler
from .forms import SettingsForm
from .utils import save_config, load_config
from .stripe_handler import StripeHandler

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin.login'))
        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    products = Product.query.all()
    config = load_config()
    is_configured = all(config['woocommerce'].values()) and all(config['stripe'].values())
    return render_template('admin/dashboard.html', products=products, is_configured=is_configured)

@admin_bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    config = load_config()
    
    if not all(config['woocommerce'].values()) or not all(config['stripe'].values()):
        flash('WooCommerce or Stripe is not configured. Please configure them in the settings.', 'warning')
        return redirect(url_for('admin.settings'))

    woo_handler = WooCommerceHandler(config['woocommerce'])
    stripe_handler = StripeHandler(config['stripe']['api_key'], config['stripe']['webhook_secret'])
    
    try:
        woo_products = woo_handler.get_all_products()
        stripe_products = stripe_handler.get_all_products()
        
        form.woo_product_ids.choices = [(p['id'], p['name']) for p in woo_products]
        form.stripe_product_id.choices = [(p['id'], p['name']) for p in stripe_products]
    except Exception as e:
        flash(f'Error fetching products: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

    if form.validate_on_submit():
        product = Product(
            stripe_id=form.stripe_product_id.data,
            name=form.name.data
        )
        product.set_woo_product_ids(form.woo_product_ids.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/product_form.html', form=form, title="New Product")

@admin_bp.route('/product/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    config = load_config()
    if not all(config['woocommerce'].values()) or not all(config['stripe'].values()):
        flash('WooCommerce or Stripe is not configured. Please configure them in the settings.', 'warning')
        return redirect(url_for('admin.settings'))

    woo_handler = WooCommerceHandler(config['woocommerce'])
    stripe_handler = StripeHandler(config['stripe']['api_key'], config['stripe']['webhook_secret'])
    
    try:
        woo_products = woo_handler.get_all_products()
        stripe_products = stripe_handler.get_all_products()
        
        form.woo_product_ids.choices = [(str(p['id']), p['name']) for p in woo_products]
        form.stripe_product_id.choices = [(p['id'], p['name']) for p in stripe_products]
    except Exception as e:
        flash(f'Error fetching products: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

    if form.validate_on_submit():
        product.stripe_id = form.stripe_product_id.data
        product.name = form.name.data
        product.set_woo_product_ids(form.woo_product_ids.data)
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    form.woo_product_ids.data = product.get_woo_product_ids()
    form.stripe_product_id.data = product.stripe_id
    return render_template('admin/product_form.html', form=form, title="Edit Product")

@admin_bp.route('/product/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        new_config = {
            'woocommerce': {
                'url': form.woo_url.data,
                'consumer_key': form.woo_consumer_key.data,
                'consumer_secret': form.woo_consumer_secret.data
            },
            'stripe': {
                'api_key': form.stripe_api_key.data,
                'webhook_secret': form.stripe_webhook_secret.data
            }
        }
        save_config(new_config)
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
    
    # Pre-fill form with current settings
    config = load_config()
    form.woo_url.data = config['woocommerce']['url']
    form.woo_consumer_key.data = config['woocommerce']['consumer_key']
    form.woo_consumer_secret.data = config['woocommerce']['consumer_secret']
    form.stripe_api_key.data = config['stripe']['api_key']
    form.stripe_webhook_secret.data = config['stripe']['webhook_secret']
    
    return render_template('admin/settings.html', form=form)
