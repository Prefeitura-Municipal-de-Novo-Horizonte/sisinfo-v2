"""
Conexão com MongoDB para logs de auditoria.
"""
from pymongo import MongoClient
from decouple import config
import logging
import certifi

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """
    Singleton para conexão com MongoDB.
    Usa a variável DATABASE_MONGODB_LOGS do .env
    """
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                connection_string = config('DATABASE_MONGODB_LOGS')
                
                client_options = {
                    'serverSelectionTimeoutMS': 2000,
                    'connectTimeoutMS': 2000,
                    'socketTimeoutMS': 2000,
                }
                
                # Configurar SSL/TLS apenas se não for localhost
                if 'localhost' not in connection_string and '127.0.0.1' not in connection_string:
                    client_options['tlsCAFile'] = certifi.where()
                    # Workaround para SSL no Vercel (Python 3.13 compatibility issue)
                    client_options['tlsInsecure'] = True
                    
                cls._client = MongoClient(connection_string, **client_options)
                logger.debug("Cliente MongoDB inicializado (lazy)")
            except Exception as e:
                logger.error(f"Erro ao inicializar MongoDB: {e}")
                cls._client = None
        return cls._instance
    
    @property
    def db(self):
        """Retorna database sisinfo_audit"""
        if self._client is not None:
            return self._client.sisinfo_audit
        return None
    
    @property
    def logs(self):
        """Retorna collection audit_logs"""
        if self._client is not None:
            return self._client.sisinfo_audit.audit_logs
        return None
    
    def close(self):
        """Fecha conexão com MongoDB"""
        if self._client:
            self._client.close()
            logger.info("Conexão MongoDB fechada")
