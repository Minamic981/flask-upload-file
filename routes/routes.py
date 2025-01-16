from flask import render_template
from routes import routes_bp

@routes_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")