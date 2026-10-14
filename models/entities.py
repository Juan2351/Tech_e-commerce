from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Product:
    id_producto: str
    nombre: str
    descripcion: str
    precio: Decimal
    rating: Decimal
    reviews_count: int
    stock: int
    url: str
    image_url: str
    id_marca: int
    id_subcat: int
    marca: str
    subcategoria: str
    categoria: str
    id_main_cat: int

    @classmethod
    def from_row(cls, row):
        return cls(
            id_producto=row["id_producto"],
            nombre=row["nombre"],
            descripcion=row["descripcion"] or "",
            precio=Decimal(row["precio"]),
            rating=Decimal(row["rating"]),
            reviews_count=row["reviews_count"],
            stock=row["stock"],
            url=row["url"] or "",
            image_url=row["image_url"] or "",
            id_marca=row["id_marca"],
            id_subcat=row["id_subcat"],
            marca=row["marca"],
            subcategoria=row["subcategoria"],
            categoria=row["categoria"],
            id_main_cat=row["id_main_cat"],
        )

    def to_dict(self, usd_to_cop_rate):
        price_cop = (self.precio * usd_to_cop_rate).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio_base_usd": str(self.precio),
            "precio": int(price_cop),
            "moneda": "COP",
            "rating": str(self.rating),
            "reviews_count": self.reviews_count,
            "stock": self.stock,
            "url": self.url,
            "image_url": self.image_url,
            "marca": self.marca,
            "subcategoria": self.subcategoria,
            "categoria": self.categoria,
        }
