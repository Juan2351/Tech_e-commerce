from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
import mysql.connector

from configs.settings import BASE_DIR, Config
from controllers.api_controller import api
from controllers.shop_controller import shop
from models.database import DatabaseConfigurationError, close_db


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    try:
        exchange_rate = Decimal(str(app.config["USD_TO_COP_RATE"]))
    except (InvalidOperation, TypeError, ValueError):
        raise RuntimeError("USD_TO_COP_RATE debe ser una tasa numérica positiva.") from None
    if not exchange_rate.is_finite() or exchange_rate <= 0:
        raise RuntimeError("USD_TO_COP_RATE debe ser una tasa numérica positiva.")
    app.config["USD_TO_COP_RATE"] = exchange_rate

    app.register_blueprint(shop)
    app.register_blueprint(api)
    app.teardown_appcontext(close_db)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": {
                    "code": error.name.lower().replace(" ", "_"),
                    "message": error.description,
                }
            }), error.code
        return render_template("error.html", message=error.description), error.code

    @app.errorhandler(DatabaseConfigurationError)
    @app.errorhandler(mysql.connector.Error)
    def handle_database_error(error):
        app.logger.exception("La operación requiere una base de datos disponible.")
        message = "No fue posible conectar con la base de datos. Revisa la configuración."
        if request.path.startswith("/api/"):
            return jsonify({
                "error": {"code": "database_unavailable", "message": message}
            }), 503
        return render_template("error.html", message=message), 503

    return app


app = create_app()


if __name__ == "__main__":
    cert = app.config["SSL_CERT_FILE"]
    key = app.config["SSL_KEY_FILE"]
    if bool(cert) != bool(key):
        raise RuntimeError("Configura juntos SSL_CERT_FILE y SSL_KEY_FILE.")
    ssl_context = (cert, key) if cert and key else None
    app.run(host="127.0.0.1", port=5000, debug=True, ssl_context=ssl_context)
