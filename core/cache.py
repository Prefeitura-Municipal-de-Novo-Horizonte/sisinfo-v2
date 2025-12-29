"""
Cache abstrato que usa Redis local (dev) ou Upstash REST API (prod).

Uso:
    from core.cache import cache_get, cache_set, cache_delete

    # Cachear dados
    cache_set("dashboard_stats", data, ttl=300)

    # Recuperar
    data = cache_get("dashboard_stats")

    # Invalidar
    cache_delete("dashboard_stats")
"""
import json
import logging

from decouple import config

logger = logging.getLogger(__name__)

# Detecta ambiente
UPSTASH_URL = config("UPSTASH_REDIS_REST_URL", default="")
UPSTASH_TOKEN = config("UPSTASH_REDIS_REST_TOKEN", default="")
USE_REDIS = config("USE_REDIS", default=False, cast=bool)
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

# Cliente Redis (inicializado sob demanda)
_redis_client = None


def _get_client():
    """Retorna cliente Redis apropriado para o ambiente."""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if UPSTASH_URL and UPSTASH_TOKEN:
        # Produção - Upstash REST API
        try:
            from upstash_redis import Redis
            _redis_client = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
            logger.info("Cache: Usando Upstash REST API")
        except ImportError:
            logger.warning("upstash-redis não instalado, cache desabilitado")
            _redis_client = None
    elif USE_REDIS:
        # Desenvolvimento - Docker Redis
        try:
            import redis
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            # Testa conexão
            _redis_client.ping()
            logger.info("Cache: Usando Redis local (Docker)")
        except Exception as e:
            logger.warning(f"Redis local não disponível: {e}")
            _redis_client = None
    else:
        logger.info("Cache: Desabilitado (sem Redis configurado)")
        _redis_client = None

    return _redis_client


def cache_get(key: str):
    """
    Recupera valor do cache.

    Args:
        key: Chave do cache

    Returns:
        Valor deserializado ou None se não encontrado
    """
    client = _get_client()
    if not client:
        return None

    try:
        value = client.get(key)
        if value:
            return json.loads(value) if isinstance(value, str) else value
        return None
    except Exception as e:
        logger.warning(f"Erro ao ler cache [{key}]: {e}")
        return None


def cache_set(key: str, value, ttl: int = 300):
    """
    Armazena valor no cache.

    Args:
        key: Chave do cache
        value: Valor a armazenar (será serializado para JSON)
        ttl: Tempo de vida em segundos (padrão: 5 minutos)
    """
    client = _get_client()
    if not client:
        return

    try:
        serialized = json.dumps(value, default=str)
        client.set(key, serialized, ex=ttl)
    except Exception as e:
        logger.warning(f"Erro ao escrever cache [{key}]: {e}")


def cache_delete(key: str):
    """
    Remove chave do cache.

    Args:
        key: Chave a remover
    """
    client = _get_client()
    if not client:
        return

    try:
        client.delete(key)
    except Exception as e:
        logger.warning(f"Erro ao deletar cache [{key}]: {e}")


def cache_clear_pattern(pattern: str):
    """
    Remove todas as chaves que correspondem ao padrão.

    Args:
        pattern: Padrão glob (ex: "dashboard_*")
    """
    client = _get_client()
    if not client:
        return

    try:
        # Upstash não suporta SCAN, usa KEYS (ok para poucos dados)
        keys = client.keys(pattern)
        if keys:
            for key in keys:
                client.delete(key)
    except Exception as e:
        logger.warning(f"Erro ao limpar cache [{pattern}]: {e}")


# Constantes de chaves de cache
CACHE_DASHBOARD_STATS = "dashboard_stats"
CACHE_DASHBOARD_CHARTS = "dashboard_charts"
CACHE_SUPPLIERS_LIST = "suppliers_list"
CACHE_SECTORS_LIST = "sectors_list"
CACHE_DIRECTIONS_LIST = "directions_list"
CACHE_MATERIALS_LIST = "materials_list"
CACHE_BIDDINGS_LIST = "biddings_list"

# TTLs padrão (em segundos)
TTL_SHORT = 60        # 1 minuto
TTL_MEDIUM = 300      # 5 minutos
TTL_LONG = 1800       # 30 minutos
TTL_HOUR = 3600       # 1 hora


class CachedLists:
    """
    Cache para listas frequentemente acessadas.
    
    Uso:
        # Na view
        suppliers = CachedLists.get_suppliers()
        
        # Ao criar/editar/deletar
        CachedLists.invalidate_suppliers()
    """
    
    @staticmethod
    def get_suppliers():
        """Retorna lista de fornecedores (cacheada por 30 min)."""
        from bidding_supplier.models import Supplier
        
        cached = cache_get(CACHE_SUPPLIERS_LIST)
        if cached:
            return cached
        
        # Query otimizada
        data = list(Supplier.objects.values('id', 'trade', 'cnpj', 'slug').order_by('trade'))
        cache_set(CACHE_SUPPLIERS_LIST, data, ttl=TTL_LONG)
        return data
    
    @staticmethod
    def get_sectors():
        """Retorna lista de setores (cacheada por 30 min)."""
        from organizational_structure.models import Sector
        
        cached = cache_get(CACHE_SECTORS_LIST)
        if cached:
            return cached
        
        data = list(Sector.objects.select_related('direction').values(
            'id', 'name', 'slug', 'direction__name'
        ).order_by('name'))
        cache_set(CACHE_SECTORS_LIST, data, ttl=TTL_LONG)
        return data
    
    @staticmethod
    def get_directions():
        """Retorna lista de diretorias (cacheada por 30 min)."""
        from organizational_structure.models import Direction
        
        cached = cache_get(CACHE_DIRECTIONS_LIST)
        if cached:
            return cached
        
        data = list(Direction.objects.values('id', 'name', 'slug').order_by('name'))
        cache_set(CACHE_DIRECTIONS_LIST, data, ttl=TTL_LONG)
        return data
    
    @staticmethod
    def get_materials():
        """Retorna lista de materiais (cacheada por 30 min)."""
        from bidding_procurement.models import Material
        
        cached = cache_get(CACHE_MATERIALS_LIST)
        if cached:
            return cached
        
        data = list(Material.objects.values('id', 'name', 'slug').order_by('name'))
        cache_set(CACHE_MATERIALS_LIST, data, ttl=TTL_LONG)
        return data
    
    @staticmethod
    def get_biddings_active():
        """Retorna lista de licitações ativas (cacheada por 30 min)."""
        from bidding_procurement.models import Bidding
        
        cached = cache_get(CACHE_BIDDINGS_LIST)
        if cached:
            return cached
        
        data = list(Bidding.objects.filter(status='1').values(
            'id', 'name', 'slug', 'number_bidding'
        ).order_by('name'))
        cache_set(CACHE_BIDDINGS_LIST, data, ttl=TTL_LONG)
        return data
    
    # --- Invalidação ---
    
    @staticmethod
    def invalidate_suppliers():
        """Invalida cache de fornecedores."""
        cache_delete(CACHE_SUPPLIERS_LIST)
    
    @staticmethod
    def invalidate_sectors():
        """Invalida cache de setores."""
        cache_delete(CACHE_SECTORS_LIST)
    
    @staticmethod
    def invalidate_directions():
        """Invalida cache de diretorias."""
        cache_delete(CACHE_DIRECTIONS_LIST)
    
    @staticmethod
    def invalidate_materials():
        """Invalida cache de materiais."""
        cache_delete(CACHE_MATERIALS_LIST)
    
    @staticmethod
    def invalidate_biddings():
        """Invalida cache de licitações."""
        cache_delete(CACHE_BIDDINGS_LIST)
    
    @staticmethod
    def invalidate_all():
        """Invalida todos os caches de listas."""
        CachedLists.invalidate_suppliers()
        CachedLists.invalidate_sectors()
        CachedLists.invalidate_directions()
        CachedLists.invalidate_materials()
        CachedLists.invalidate_biddings()
