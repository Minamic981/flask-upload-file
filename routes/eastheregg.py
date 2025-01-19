from routes.routes import routes_bp
from flask import redirect

@routes_bp.route('/eastheregg')
def eastheregg():
    return redirect('https://minio-flower.chbk.app/uploads/IMG_20250119_130136.jpg', code=302)