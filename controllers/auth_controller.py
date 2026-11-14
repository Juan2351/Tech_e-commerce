from functools import wraps
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models.auth_model import AuthError, authenticate_user, register_user
from services.cart_service import switch_cart_owner

auth = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Por favor inicia sesión para acceder a esta sección.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user:
            flash("Debes iniciar sesión como administrador.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if user.get("role") != "admin":
            flash("Acceso denegado: Se requieren permisos de administrador.", "error")
            return redirect(url_for("shop.home"))
        return f(*args, **kwargs)
    return decorated_function


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        user = session["user"]
        if user.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("shop.home"))

    next_url = request.args.get("next") or request.form.get("next")
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            error = "Por favor completa todos los campos."
        else:
            user = authenticate_user(email, password)
            if user:
                rol = user.get("rol") or user.get("role", "cliente")
                nombre = user.get("nombre_usuario") or user.get("nombre", "")
                new_user_session = {
                    "id": user["id"],
                    "nombre": nombre,
                    "nombre_usuario": nombre,
                    "email": user["email"],
                    "role": rol,
                    "rol": rol,
                }
                switch_cart_owner(session, new_user_session)
                session["user"] = new_user_session
                flash(f"¡Bienvenido de nuevo, {nombre}!", "success")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                if rol == "admin":
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("shop.home"))
            else:
                error = "Correo electrónico o contraseña incorrectos."

    return render_template("auth/login.html", error=error, next_url=next_url)


@auth.route("/registro", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("shop.home"))

    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        telefono = request.form.get("telefono", "").strip()
        ciudad = request.form.get("ciudad", "").strip()

        if password != confirm_password:
            error = "Las contraseñas no coinciden. Por favor verifícalas."
        else:
            try:
                user = register_user(
                    nombre=nombre,
                    email=email,
                    password=password,
                    telefono=telefono,
                    ciudad=ciudad,
                    role="cliente",
                )
                rol = user.get("rol") or user.get("role", "cliente")
                nombre_usuario = user.get("nombre_usuario") or user.get("nombre", nombre)
                new_user_session = {
                    "id": user["id"],
                    "nombre": nombre_usuario,
                    "nombre_usuario": nombre_usuario,
                    "email": user["email"],
                    "role": rol,
                    "rol": rol,
                }
                switch_cart_owner(session, new_user_session)
                session["user"] = new_user_session
                flash("¡Registro exitoso! Bienvenido a LePetit.", "success")
                return redirect(url_for("shop.home"))
            except AuthError as err:
                error = str(err)
            except Exception:
                error = "Ocurrió un error al registrar la cuenta. Intenta nuevamente."

    return render_template("auth/register.html", error=error)


@auth.route("/logout")
def logout():
    switch_cart_owner(session, None)
    session.pop("user", None)
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("shop.home"))
