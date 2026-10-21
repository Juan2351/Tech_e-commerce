import time
from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers.auth_controller import admin_required
from models import catalog
from models.auth_model import get_all_clients, get_all_users
from models.firebase_db import FirebaseDB

admin = Blueprint("admin", __name__, url_prefix="/admin")
ADMIN_PRODUCTS_PER_PAGE = 20


@admin.route("/")
@admin.route("/dashboard")
@admin_required
def dashboard():
    stats = catalog.fetch_dashboard_stats()
    recent_products = catalog.fetch_top_products(limit=6)
    recent_clients = get_all_clients()[:5]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_products=recent_products,
        recent_clients=recent_clients,
    )


@admin.route("/productos")
@admin_required
def products_list():
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id")
    try:
        category_id = int(category_id) if category_id else None
    except ValueError:
        category_id = None

    page = request.args.get("page", 1)
    try:
        page = max(1, int(page))
    except ValueError:
        page = 1

    all_products = catalog.fetch_products(
        category_id=category_id,
        search=search,
        sort="featured"
    )
    total_products = len(all_products)
    total_pages = max(1, (total_products + ADMIN_PRODUCTS_PER_PAGE - 1) // ADMIN_PRODUCTS_PER_PAGE)
    if page > total_pages:
        page = total_pages

    start = (page - 1) * ADMIN_PRODUCTS_PER_PAGE
    products = all_products[start:start + ADMIN_PRODUCTS_PER_PAGE]
    categories = catalog.fetch_categories()

    return render_template(
        "admin/products.html",
        products=products,
        categories=categories,
        search=search,
        category_id=category_id,
        page=page,
        total_pages=total_pages,
        total_products=total_products,
    )


@admin.route("/productos/nuevo", methods=["GET", "POST"])
@admin_required
def product_create():
    categories = catalog.fetch_categories()
    subcategories = catalog.fetch_subcategories()
    error = None

    if request.method == "POST":
        p_id = request.form.get("id_producto", "").strip()
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = request.form.get("precio", "0").strip()
        stock = request.form.get("stock", "0").strip()
        rating = request.form.get("rating", "4.5").strip()
        reviews_count = request.form.get("reviews_count", "1").strip()
        marca = request.form.get("marca", "LePetit").strip()
        categoria_id = request.form.get("id_main_cat", "1").strip()
        subcat_id = request.form.get("id_subcat", "1").strip()
        image_url = request.form.get("image_url", "").strip()
        url = request.form.get("url", "").strip()

        if not p_id or not nombre or not precio:
            error = "ID, Nombre y Precio son campos obligatorios."
        else:
            try:
                # Buscar nombres de categoría y subcategoría
                cat_name = next(
                    (c["nombre"] for c in categories if str(c["id_main_cat"]) == str(categoria_id)),
                    "Tecnología"
                )
                subcat_name = next(
                    (s["nombre"] for s in subcategories if str(s["id_subcat"]) == str(subcat_id)),
                    "General"
                )

                product_data = {
                    "id_producto": p_id,
                    "nombre": nombre,
                    "descripcion": descripcion or f"{nombre}. Producto garantizado.",
                    "precio": float(precio),
                    "stock": int(stock),
                    "rating": float(rating),
                    "reviews_count": int(reviews_count),
                    "marca": marca,
                    "id_marca": 1,
                    "id_main_cat": int(categoria_id),
                    "categoria": cat_name,
                    "id_subcat": int(subcat_id),
                    "subcategoria": subcat_name,
                    "image_url": image_url,
                    "url": url,
                }
                catalog.save_product(product_data)
                flash(f"Producto '{nombre}' creado exitosamente en Firebase.", "success")
                return redirect(url_for("admin.products_list"))
            except Exception as err:
                error = f"Error al guardar producto: {err}"

    return render_template(
        "admin/product_form.html",
        action="Crear",
        product=None,
        categories=categories,
        subcategories=subcategories,
        error=error,
    )


@admin.route("/productos/editar/<string:product_id>", methods=["GET", "POST"])
@admin_required
def product_edit(product_id):
    product = catalog.fetch_product(product_id)
    if not product:
        flash("El producto no existe.", "error")
        return redirect(url_for("admin.products_list"))

    categories = catalog.fetch_categories()
    subcategories = catalog.fetch_subcategories()
    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = request.form.get("precio", "0").strip()
        stock = request.form.get("stock", "0").strip()
        rating = request.form.get("rating", "4.5").strip()
        reviews_count = request.form.get("reviews_count", "1").strip()
        marca = request.form.get("marca", "LePetit").strip()
        categoria_id = request.form.get("id_main_cat", "1").strip()
        subcat_id = request.form.get("id_subcat", "1").strip()
        image_url = request.form.get("image_url", "").strip()
        url = request.form.get("url", "").strip()

        if not nombre or not precio:
            error = "Nombre y Precio son campos obligatorios."
        else:
            try:
                cat_name = next(
                    (c["nombre"] for c in categories if str(c["id_main_cat"]) == str(categoria_id)),
                    product.categoria
                )
                subcat_name = next(
                    (s["nombre"] for s in subcategories if str(s["id_subcat"]) == str(subcat_id)),
                    product.subcategoria
                )

                product_data = {
                    "id_producto": product.id_producto,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": float(precio),
                    "stock": int(stock),
                    "rating": float(rating),
                    "reviews_count": int(reviews_count),
                    "marca": marca,
                    "id_marca": product.id_marca,
                    "id_main_cat": int(categoria_id),
                    "categoria": cat_name,
                    "id_subcat": int(subcat_id),
                    "subcategoria": subcat_name,
                    "image_url": image_url,
                    "url": url,
                }
                catalog.save_product(product_data)
                flash(f"Producto '{nombre}' actualizado exitosamente en Firebase.", "success")
                return redirect(url_for("admin.products_list"))
            except Exception as err:
                error = f"Error al actualizar producto: {err}"

    return render_template(
        "admin/product_form.html",
        action="Editar",
        product=product,
        categories=categories,
        subcategories=subcategories,
        error=error,
    )


@admin.route("/productos/eliminar/<string:product_id>", methods=["POST"])
@admin_required
def product_delete(product_id):
    try:
        catalog.delete_product(product_id)
        flash(f"Producto con ID {product_id} eliminado exitosamente de Firebase.", "success")
    except Exception as err:
        flash(f"Error al eliminar producto: {err}", "error")
    return redirect(url_for("admin.products_list"))


@admin.route("/categorias", methods=["GET", "POST"])
@admin_required
def categories_manage():
    error = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            if not nombre:
                error = "El nombre de la categoría es requerido."
            else:
                existing = catalog.fetch_categories()
                max_id = max([int(c.get("id_main_cat", 0)) for c in existing] or [0])
                new_cat = {
                    "id_main_cat": max_id + 1,
                    "nombre": nombre,
                    "descripcion": descripcion or f"Categoría de productos {nombre}.",
                    "imagen": "",
                }
                catalog.save_category(new_cat)
                flash(f"Categoría '{nombre}' creada exitosamente en Firebase.", "success")
                return redirect(url_for("admin.categories_manage"))

        elif action == "edit":
            cat_id = request.form.get("id_main_cat")
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            if cat_id and nombre:
                catalog.save_category({
                    "id_main_cat": int(cat_id),
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "imagen": "",
                })
                flash("Categoría actualizada correctamente.", "success")
                return redirect(url_for("admin.categories_manage"))

        elif action == "delete":
            cat_id = request.form.get("id_main_cat")
            if cat_id:
                catalog.delete_category(int(cat_id))
                flash("Categoría eliminada de Firebase.", "success")
                return redirect(url_for("admin.categories_manage"))

    categories = catalog.fetch_categories()
    products_raw = FirebaseDB.get_all_products_raw()
    
    # Calcular conteo de productos por categoría
    category_counts = {}
    for p in products_raw.values():
        cid = p.get("id_main_cat")
        if cid is not None:
            category_counts[cid] = category_counts.get(cid, 0) + 1

    return render_template(
        "admin/categories.html",
        categories=categories,
        category_counts=category_counts,
        error=error,
    )


@admin.route("/clientes")
@admin_required
def clients_list():
    users = get_all_users()
    return render_template("admin/clients.html", users=users)
