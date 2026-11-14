from decimal import Decimal, InvalidOperation
import secrets
import sqlite3

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.exceptions import HTTPException
from flask_swagger_ui import get_swaggerui_blueprint

from configs.settings import BASE_DIR, Config
from controllers.admin_controller import admin
from controllers.api_controller import api
from controllers.auth_controller import auth
from controllers.shop_controller import shop
from extensions import jwt
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
    if not app.config.get("JWT_SECRET_KEY"):
        app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]
    try:
        exchange_rate = Decimal(str(app.config["USD_TO_COP_RATE"]))
    except (InvalidOperation, TypeError, ValueError):
        raise RuntimeError("USD_TO_COP_RATE debe ser una tasa numérica positiva.") from None
    if not exchange_rate.is_finite() or exchange_rate <= 0:
        raise RuntimeError("USD_TO_COP_RATE debe ser una tasa numérica positiva.")
    app.config["USD_TO_COP_RATE"] = exchange_rate

    jwt.init_app(app)
    app.register_blueprint(shop)
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(
        get_swaggerui_blueprint(
            "/api/docs",
            "/api/openapi.yaml",
            config={"app_name": "LePetit API"},
        )
    )
    app.teardown_appcontext(close_db)

    @app.before_request
    def protect_csrf_forms():
        if request.method != "POST":
            return None
        if request.path.startswith("/api/") or request.path.startswith("/admin/analytics/"):
            return None
        csrf_enabled = app.config.get("CSRF_ENABLED", not app.config.get("TESTING", False))
        submitted_token = request.form.get("csrf_token")
        expected_token = session.get("_csrf_token", "")
        if submitted_token is not None or csrf_enabled:
            if (
                not isinstance(submitted_token, str)
                or not isinstance(expected_token, str)
                or not expected_token
                or not secrets.compare_digest(submitted_token, expected_token)
            ):
                abort(400, description="Token de seguridad CSRF inválido o vencido. Recarga la página e inténtalo de nuevo.")
        return None

    @app.before_request
    def protect_admin_analytics():
        if not request.path.startswith("/admin/analytics"):
            return None
        user = session.get("user")
        if user and user.get("role") == "admin":
            return None
        if request.path.startswith("/admin/analytics/_dash"):
            return jsonify({
                "error": {
                    "code": "forbidden" if user else "authentication_required",
                    "message": "Se requieren permisos de administrador.",
                }
            }), 403 if user else 401
        return redirect(url_for("auth.login", next=request.url))

    @app.get("/api/openapi.yaml")
    def serve_openapi_spec():
        return send_from_directory(
            BASE_DIR / "docs", "openapi.yaml", mimetype="application/yaml"
        )

    from controllers.admin_dash import init_admin_dash
    app.extensions["admin_dash"] = init_admin_dash(app)

    @app.context_processor
    def inject_auth_context():
        from flask import session
        user = session.get("user")
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return {
            "current_user": user,
            "is_admin": user.get("role") == "admin" if user else False,
            "csrf_token": session["_csrf_token"],
            "firebase_config": {
                "apiKey": app.config.get("FIREBASE_API_KEY", ""),
                "authDomain": app.config.get("FIREBASE_AUTH_DOMAIN", ""),
                "databaseURL": app.config.get("FIREBASE_DATABASE_URL", ""),
                "projectId": app.config.get("FIREBASE_PROJECT_ID", ""),
                "storageBucket": app.config.get("FIREBASE_STORAGE_BUCKET", ""),
            }
        }

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
    @app.errorhandler(sqlite3.Error)
    def handle_database_error(error):
        app.logger.exception("No fue posible consultar la base de datos local.")
        message = "No fue posible abrir la base de datos local. Revisa el catálogo CSV."
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
