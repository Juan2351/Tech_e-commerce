from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re


_MODEL_3D_RULES = (
    ("laptop", "Portátil 3D", re.compile(r"laptop|notebook|port[aá]til", re.IGNORECASE)),
    (
        "phone",
        "Smartphone / Tablet 3D",
        re.compile(
            r"smartphone|iphone|(?:^|[^a-z])phones?(?:$|[^a-z])|tel[eé]fono|tablet|e-ink",
            re.IGNORECASE,
        ),
    ),
    ("monitor", "Monitor 3D", re.compile(r"monitor|display|pantalla", re.IGNORECASE)),
    (
        "desktop",
        "PC / Mini PC 3D",
        re.compile(
            r"desktop|mini pc|all-in-one|computador de escritorio|pc de escritorio",
            re.IGNORECASE,
        ),
    ),
    (
        "audio",
        "Audio 3D",
        re.compile(
            r"headphones?|headsets?|earbuds?|auriculares?|audio|aud[ií]fonos?",
            re.IGNORECASE,
        ),
    ),
    ("wearable", "Smartwatch 3D", re.compile(r"watch|wearable|reloj", re.IGNORECASE)),
    ("peripheral", "Teclado 3D", re.compile(r"keyboard|teclado", re.IGNORECASE)),
    ("mouse", "Mouse 3D", re.compile(r"mice|mouse|rat[oó]n", re.IGNORECASE)),
    ("hub", "Hub / Dock 3D", re.compile(r"hub|dock", re.IGNORECASE)),
    ("storage", "Almacenamiento 3D", re.compile(r"ssd|storage|network|power", re.IGNORECASE)),
)


def resolve_3d_model_info(category_text: str):
    text = (category_text or "").strip()
    for model_type, label, pattern in _MODEL_3D_RULES:
        if pattern.search(text):
            return model_type, label, True
    return "generic", "Esquemático 3D", False


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

    @property
    def model_3d_type(self) -> str:
        model_type, _, _ = resolve_3d_model_info(f"{self.subcategoria} {self.categoria}")
        return model_type

    @property
    def model_3d_label(self) -> str:
        _, label, _ = resolve_3d_model_info(f"{self.subcategoria} {self.categoria}")
        return label

    @property
    def has_3d_model(self) -> bool:
        _, _, has_dedicated = resolve_3d_model_info(f"{self.subcategoria} {self.categoria}")
        return has_dedicated

    @classmethod
    def from_row(cls, row):
        return cls(
            id_producto=row["id_producto"],
            nombre=row["nombre"],
            descripcion=row["descripcion"] or "",
            precio=Decimal(str(row["precio"])),
            rating=Decimal(str(row["rating"])),
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
            "has_3d_model": self.has_3d_model,
            "model_3d_type": self.model_3d_type,
            "model_3d_label": self.model_3d_label,
        }
