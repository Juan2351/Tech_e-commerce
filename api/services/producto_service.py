"""
Servicio de Producto
Logica de negocio, validacion de reglas y construccion de consultas para productos.
"""

from api.models.producto_model import ProductoModel

SORT_COLUMNS = {
    "price_asc":    "p.precio ASC",
    "price_desc":   "p.precio DESC",
    "rating_desc":  "p.rating DESC",
    "reviews_desc": "p.reviews_count DESC",
    "stock_desc":   "p.stock DESC",
}

class ProductoService:
    @staticmethod
    def listar_productos(args):
        # 1. Paginacion
        try:
            page = max(1, int(args.get("page", 1)))
        except ValueError:
            page = 1

        try:
            limit = min(100, max(1, int(args.get("limit", 24))))
        except ValueError:
            limit = 24

        offset = (page - 1) * limit

        # 2. Parametros de filtrado
        marca = args.get("marca", "").strip()
        categoria = args.get("categoria", "").strip()
        subcategoria = args.get("subcategoria", "").strip()
        min_rating_str = args.get("min_rating", "0").strip()
        q = args.get("q", "").strip()
        sort_key = args.get("sort", "").strip()

        sort_col = SORT_COLUMNS.get(sort_key, "p.id_producto ASC")

        conditions = ["1=1"]
        params = []

        if marca:
            conditions.append("m.nombre = %s")
            params.append(marca)

        if categoria:
            conditions.append("c.nombre = %s")
            params.append(categoria)

        if subcategoria:
            conditions.append("s.nombre = %s")
            params.append(subcategoria)

        try:
            min_rating = float(min_rating_str)
            if min_rating > 0:
                conditions.append("p.rating >= %s")
                params.append(min_rating)
        except ValueError:
            pass

        if q:
            conditions.append("(p.descripcion LIKE %s OR m.nombre LIKE %s OR s.nombre LIKE %s)")
            like_term = f"%{q}%"
            params.extend([like_term, like_term, like_term])

        # 3. Consulta a la capa de datos
        productos = ProductoModel.find_all(conditions, params, sort_col=sort_col, limit=limit, offset=offset)
        total = ProductoModel.count(conditions, params)

        total_pages = -(-total // limit) if total > 0 else 1

        return {
            "data": productos,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages
        }

    @staticmethod
    def obtener_por_id(id_producto):
        if not id_producto:
            return None, "ID de producto no proporcionado"
        producto = ProductoModel.find_by_id(id_producto.strip())
        if not producto:
            return None, "Producto no encontrado"
        return producto, None

    @staticmethod
    def crear_producto(data):
        # Validaciones de regla de negocio
        id_prod = data.get("id_producto", "").strip()
        desc = data.get("descripcion", "").strip()
        precio = data.get("precio")

        if not id_prod:
            return None, "El campo 'id_producto' es obligatorio."
        if not desc:
            return None, "El campo 'descripcion' es obligatorio."
        if precio is None:
            return None, "El campo 'precio' es obligatorio."

        try:
            precio_val = float(precio)
            if precio_val <= 0:
                return None, "El precio debe ser un numero positivo mayor a cero."
        except ValueError:
            return None, "El precio ingresado no es valido."

        # Verificar existencia previa
        existente = ProductoModel.find_by_id(id_prod)
        if existente:
            return None, f"Ya existe un producto con el ID '{id_prod}'."

        ProductoModel.create(data)
        return ProductoModel.find_by_id(id_prod), None

    @staticmethod
    def actualizar_producto(id_producto, data):
        existente = ProductoModel.find_by_id(id_producto)
        if not existente:
            return None, "Producto no encontrado"

        allowed_fields = ["descripcion", "precio", "rating", "reviews_count", "stock", "url", "image_url", "id_marca", "id_subcat"]
        updates = {}

        for field in allowed_fields:
            if field in data:
                if field == "precio":
                    try:
                        p = float(data["precio"])
                        if p <= 0:
                            return None, "El precio debe ser mayor a cero."
                        updates["precio"] = p
                    except ValueError:
                        return None, "Precio invalido."
                elif field == "stock":
                    try:
                        s = int(data["stock"])
                        if s < 0:
                            return None, "El stock no puede ser negativo."
                        updates["stock"] = s
                    except ValueError:
                        return None, "Stock invalido."
                else:
                    updates[field] = data[field]

        if not updates:
            return None, "No se proporcionaron campos validos para actualizar."

        ProductoModel.update(id_producto, updates)
        return ProductoModel.find_by_id(id_producto), None

    @staticmethod
    def eliminar_producto(id_producto):
        existente = ProductoModel.find_by_id(id_producto)
        if not existente:
            return False, "Producto no encontrado"
        ProductoModel.delete(id_producto)
        return True, None
