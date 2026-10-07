"""
Amazon Tech Products - API RESTful
Arquitectura Modelo-Vista-Controlador (MVC) en 3 Capas
Ejecutar: python app.py
"""

from pathlib import Path
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS

ROOT_DIR = Path(__file__).resolve().parent

from config.config import Config
from controllers.productos_controller import productos_bp
from controllers.marcas_controller import marcas_bp
from controllers.categorias_controller import categorias_bp
from controllers.estadisticas_controller import estadisticas_bp
from controllers.salud_controller import salud_bp
from models.database import get_engine


def create_app():
    """Fabrica de la aplicacion Flask."""
    app = Flask(
        __name__,
        template_folder=str(ROOT_DIR / "templates"),
        static_folder=str(ROOT_DIR / "static"),
    )

    # 1. Habilitar CORS
    CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

    # 2. Registrar Blueprints (Controladores)
    app.register_blueprint(productos_bp)
    app.register_blueprint(marcas_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(salud_bp)

    # 3. Ruta principal informativa
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/api", methods=["GET"])
    def api_info():
        return jsonify({
            "nombre": "Amazon Tech Products REST API",
            "version": "v1",
            "arquitectura": "MVC (Modelo-Vista-Controlador)",
            "motor_bd": get_engine(),
            "endpoints": {
                "salud": "/api/v1/salud",
                "estadisticas": "/api/v1/estadisticas",
                "marcas": "/api/v1/marcas",
                "categorias": "/api/v1/categorias",
                "productos": "/api/v1/productos"
            }
        }), 200

    @app.route("/conjunto_datos/<path:filename>", methods=["GET"])
    def dataset(filename):
        return send_from_directory(ROOT_DIR / "conjunto_datos", filename)

    # 4. Manejadores de errores globales
    @app.errorhandler(404)
    def no_encontrado(e):
        return jsonify({"error": "Recurso no encontrado", "codigo": 404}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(e):
        return jsonify({"error": "Metodo HTTP no permitido", "codigo": 405}), 405

    @app.errorhandler(500)
    def error_servidor(e):
        return jsonify({"error": "Error interno del servidor", "codigo": 500}), 500

    return app


app = create_app()

if __name__ == "__main__":
    motor = get_engine()
    print("=" * 60)
    print(" Amazon Tech Products E-Commerce - API RESTful v1")
    print(f" Arquitectura: MVC de 3 Capas")
    print(f" Motor Activo de Base de Datos: {motor}")
    print(f" Host: http://localhost:{Config.FLASK_PORT}")
    print("=" * 60)
    print(f" - Diagnostico:   GET http://localhost:{Config.FLASK_PORT}/api/v1/salud")
    print(f" - Estadisticas:  GET http://localhost:{Config.FLASK_PORT}/api/v1/estadisticas")
    print(f" - Marcas:        GET http://localhost:{Config.FLASK_PORT}/api/v1/marcas")
    print(f" - Categorias:    GET http://localhost:{Config.FLASK_PORT}/api/v1/categorias")
    print(f" - Productos:     GET http://localhost:{Config.FLASK_PORT}/api/v1/productos")
    print("=" * 60)

    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
