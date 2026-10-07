"""
Servicio de Catalogo
Gestiona marcas, categorias y estadisticas agregadas del catalogo.
"""

from api.models.marca_model import MarcaModel
from api.models.categoria_model import CategoriaModel
from api.models.estadisticas_model import EstadisticasModel

class CatalogoService:
    @staticmethod
    def listar_marcas():
        return MarcaModel.find_all_with_count()

    @staticmethod
    def listar_categorias():
        return CategoriaModel.find_all_nested()

    @staticmethod
    def obtener_estadisticas():
        return EstadisticasModel.get_summary()
