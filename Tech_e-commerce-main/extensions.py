from flask import jsonify
from flask_jwt_extended import JWTManager

jwt = JWTManager()


@jwt.unauthorized_loader
def missing_jwt(_reason):
    return jsonify({
        "error": {
            "code": "authentication_required",
            "message": "Se requiere un token Bearer válido.",
        }
    }), 401


@jwt.invalid_token_loader
def invalid_jwt(_reason):
    return jsonify({
        "error": {
            "code": "invalid_token",
            "message": "El token de acceso no es válido.",
        }
    }), 401


@jwt.expired_token_loader
def expired_jwt(_header, _payload):
    return jsonify({
        "error": {
            "code": "expired_token",
            "message": "El token de acceso ha expirado.",
        }
    }), 401
