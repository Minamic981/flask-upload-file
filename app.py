from flask import Flask
from routes import routes_bp
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv()
# Register Blueprint
# s
app.register_blueprint(routes_bp)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)