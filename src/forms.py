from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import ListWidget, CheckboxInput

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    stripe_product_id = SelectField('Stripe Product', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    woo_product_ids = SelectMultipleField('WooCommerce Products', 
                                          coerce=int,
                                          option_widget=CheckboxInput(),
                                          widget=ListWidget(prefix_label=False))
    submit = SubmitField('Submit')

class SettingsForm(FlaskForm):
    woo_url = StringField('WooCommerce URL', validators=[DataRequired()])
    woo_consumer_key = StringField('WooCommerce Consumer Key', validators=[DataRequired()])
    woo_consumer_secret = StringField('WooCommerce Consumer Secret', validators=[DataRequired()])
    stripe_api_key = StringField('Stripe API Key', validators=[DataRequired()])
    stripe_webhook_secret = StringField('Stripe Webhook Secret', validators=[DataRequired()])
    submit = SubmitField('Save Settings')
