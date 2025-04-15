from flask import Flask
from models import init_db
from views import bp as api_bp  # <-- asegurarte de importar el blueprint

def create_app():
    app = Flask(__name__)
    init_db()  # conecta con la base de datos
    app.register_blueprint(api_bp)  # <-- esto es lo que activa las rutas
    return app
