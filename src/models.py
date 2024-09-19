from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stripe_id = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    woo_product_ids = db.Column(db.String(256))

    def set_woo_product_ids(self, ids):
        self.woo_product_ids = ','.join(map(str, ids))

    def get_woo_product_ids(self):
        return [int(id) for id in self.woo_product_ids.split(',') if id]

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=False)

    @classmethod
    def get_value(cls, key, default=None):
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    @classmethod
    def set_value(cls, key, value):
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = cls(key=key, value=value)
            db.session.add(config)
        db.session.commit()