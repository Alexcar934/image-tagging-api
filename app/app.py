from flask import Flask
from models import init_db
from views import bp as api_bp  

def create_app():
    app = Flask(__name__)
    init_db()  # conectar con base de datos
    app.register_blueprint(api_bp)  
    return app
