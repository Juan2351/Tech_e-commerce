import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal
from typing import Any, Dict, List, Optional

from flask import current_app

logger = logging.getLogger(__name__)


class FirebaseError(Exception):
    """Excepción para errores de comunicación con Firebase Realtime Database."""
    pass


class FirebaseDB:
    """Cliente ligero para Firebase Realtime Database mediante REST API estándar.
    
    Permite operaciones CRUD directas sobre la base de datos en tiempo real de Firebase
    sin dependencias binarias pesadas, preservando la arquitectura MVC.
    """

    _cache: Dict[str, Any] = {}
    _cache_time: float = 0.0
    CACHE_TTL_SECONDS = 60.0

    @classmethod
    def _base_url(cls) -> str:
        try:
            return current_app.config.get(
                "FIREBASE_DATABASE_URL",
                "https://lepetit-e4386-default-rtdb.firebaseio.com",
            ).rstrip("/")
        except RuntimeError:
            return "https://lepetit-e4386-default-rtdb.firebaseio.com"

    @classmethod
    def request(
        cls,
        path: str,
        method: str = "GET",
        data: Optional[Any] = None,
        timeout: int = 8,
    ) -> Any:
        url = f"{cls._base_url()}/{path.strip('/')}.json"
        body_bytes = None
        headers = {"Accept": "application/json"}

        if data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            url=url,
            data=body_bytes,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                if not content or content == "null":
                    return None
                return json.loads(content)
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="ignore")
            logger.error("Error HTTP en Firebase (%s %s): %s - %s", method, url, error.code, error_body)
            raise FirebaseError(f"Error HTTP Firebase {error.code}: {error_body}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            logger.error("Error de conexión con Firebase: %s", error)
            raise FirebaseError(f"No fue posible conectar con Firebase: {error}") from error

    @classmethod
    def ping(cls) -> bool:
        """Verifica que Firebase Realtime Database responda correctamente."""
        try:
            res = cls.request("categories", method="GET", timeout=5)
            return True
        except Exception as err:
            logger.warning("Fallo al verificar Firebase: %s", err)
            return False

    @classmethod
    def invalidate_cache(cls):
        cls._cache.clear()
        cls._cache_time = 0.0

    # -------------------------------------------------------------
    # Categorías y Subcategorías
    # -------------------------------------------------------------
    @classmethod
    def get_categories(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        now = time.time()
        if not force_refresh and "categories" in cls._cache and (now - cls._cache_time < cls.CACHE_TTL_SECONDS):
            return list(cls._cache["categories"].values())

        raw = cls.request("categories") or {}
        if isinstance(raw, list):
            cats = [item for item in raw if item]
        else:
            cats = list(raw.values())

        # Asegurar orden
        cats.sort(key=lambda c: str(c.get("nombre", "")).lower())

        cls._cache["categories"] = {str(c.get("id_main_cat")): c for c in cats}
        cls._cache_time = now
        return cats

    @classmethod
    def save_category(cls, category_data: Dict[str, Any]) -> Dict[str, Any]:
        cat_id = str(category_data.get("id_main_cat"))
        cls.request(f"categories/{cat_id}", method="PUT", data=category_data)
        cls.invalidate_cache()
        return category_data

    @classmethod
    def delete_category(cls, category_id: Any) -> bool:
        cat_id = str(category_id)
        cls.request(f"categories/{cat_id}", method="DELETE")
        cls.invalidate_cache()
        return True

    @classmethod
    def get_subcategories(cls, main_category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        raw = cls.request("subcategories") or {}
        if isinstance(raw, list):
            subs = [s for s in raw if s]
        else:
            subs = list(raw.values())

        if main_category_id is not None:
            subs = [s for s in subs if str(s.get("id_main_cat")) == str(main_category_id)]

        subs.sort(key=lambda s: str(s.get("nombre", "")).lower())
        return subs

    # -------------------------------------------------------------
    # Productos
    # -------------------------------------------------------------
    @classmethod
    def get_all_products_raw(cls, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        now = time.time()
        if not force_refresh and "products" in cls._cache and (now - cls._cache_time < cls.CACHE_TTL_SECONDS):
            return cls._cache["products"]

        raw = cls.request("products") or {}
        if isinstance(raw, list):
            product_dict = {
                item["id_producto"]: item
                for item in raw
                if item and "id_producto" in item
            }
        else:
            product_dict = {
                k: v for k, v in raw.items() if isinstance(v, dict) and "id_producto" in v
            }

        cls._cache["products"] = product_dict
        cls._cache_time = now
        return product_dict

    @classmethod
    def get_product(cls, product_id: str) -> Optional[Dict[str, Any]]:
        products = cls.get_all_products_raw()
        if product_id in products:
            return products[product_id]
        # Intento directo a Firebase por si es un producto recién creado
        raw = cls.request(f"products/{product_id}")
        if raw and isinstance(raw, dict):
            cls._cache.setdefault("products", {})[product_id] = raw
            return raw
        return None

    @classmethod
    def save_product(cls, product_data: Dict[str, Any]) -> Dict[str, Any]:
        p_id = str(product_data.get("id_producto")).strip()
        # Limpieza para Firebase
        clean_data = dict(product_data)
        if "precio" in clean_data:
            clean_data["precio"] = float(clean_data["precio"])
        if "rating" in clean_data:
            clean_data["rating"] = float(clean_data["rating"])
        if "reviews_count" in clean_data:
            clean_data["reviews_count"] = int(clean_data["reviews_count"])
        if "stock" in clean_data:
            clean_data["stock"] = int(clean_data["stock"])

        cls.request(f"products/{p_id}", method="PUT", data=clean_data)
        cls.invalidate_cache()
        return clean_data

    @classmethod
    def delete_product(cls, product_id: str) -> bool:
        cls.request(f"products/{product_id}", method="DELETE")
        cls.invalidate_cache()
        return True

    # -------------------------------------------------------------
    # Usuarios / Clientes / Autenticación
    # -------------------------------------------------------------
    @classmethod
    def get_users(cls) -> List[Dict[str, Any]]:
        raw = cls.request("users") or {}
        if isinstance(raw, list):
            users = [u for u in raw if u]
        else:
            users = list(raw.values())
        return users

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        users = cls.get_users()
        for u in users:
            if str(u.get("email", "")).strip().lower() == clean_email:
                return u
        return None

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        return cls.request(f"users/{user_id}")

    @classmethod
    def save_user(cls, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = str(user_data.get("id"))
        cls.request(f"users/{user_id}", method="PUT", data=user_data)
        return user_data

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        cls.request(f"users/{user_id}", method="DELETE")
        return True
