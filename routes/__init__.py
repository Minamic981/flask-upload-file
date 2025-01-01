from flask import Blueprint

routes_bp = Blueprint('routes', __name__)

# Import all routes
from .routes import *
