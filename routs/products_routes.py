from flask import Blueprint
from controllers import products_controllers

products_bp = Blueprint('products_db', __name__)