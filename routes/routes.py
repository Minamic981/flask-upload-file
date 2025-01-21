from flask import render_template
from routes import routes_bp

@routes_bp.route("/")
def index():
    return render_template("index.html")

#Todo Must Be Changed When Done easteregg.html
@routes_bp.route("/easteregg")
def easter_egg():
    return render_template("")
