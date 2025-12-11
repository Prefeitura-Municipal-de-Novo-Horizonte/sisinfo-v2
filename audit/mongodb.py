"""
Conexão com MongoDB para logs de auditoria.
"""
from pymongo import MongoClient
from decouple import config
import logging

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
                cls._client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=5000
                )
                # Testa conexão
                cls._client.server_info()
                logger.info("MongoDB conectado com sucesso para auditoria")
            except Exception as e:
                logger.error(f"Erro ao conectar MongoDB: {e}")
                cls._client = None
        return cls._instance
    
    @property
    def db(self):
        """Retorna database sisinfo_audit"""
        if self._client:
            return self._client.sisinfo_audit
        return None
    
    @property
    def logs(self):
        """Retorna collection audit_logs"""
        if self.db:
            return self.db.audit_logs
        return None
    
    def close(self):
        """Fecha conexão com MongoDB"""
        if self._client:
            self._client.close()
            logger.info("Conexão MongoDB fechada")
