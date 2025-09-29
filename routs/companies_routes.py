from flask import Blueprint
from controllers import companies_controllers

companies_bp = Blueprint ('companies_bp', __name__)