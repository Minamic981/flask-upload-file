from routes import routes_bp
from flask import render_template
from services.s3_service import s3_client, BUCKET_NAME

@routes_bp.route('/example')
def example():
    return render_template("example.html")
