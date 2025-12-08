import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://galapagos-mongodb:27017")
DATABASE_NAME = "galapagos"

logger = logging.getLogger("uvicorn.error")


class MongoDBConnection:
    """Singleton pour la connexion MongoDB"""
    _instance = None
    _client = None
    _database = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Établir la connexion à MongoDB"""
        if self._client is None:
            self._client = AsyncIOMotorClient(MONGODB_URL)
            self._database = self._client[DATABASE_NAME]
            logger.info(f"Connecté à MongoDB: {MONGODB_URL}/{DATABASE_NAME}")
        return self._database

    async def ping(self):
        """Vérifier la connexion MongoDB"""
        try:
            # await self._client.admin.command('ping')
            logger.info(" MongoDB ping successful")
            return True
        except ConnectionFailure as e:
            logger.error(f" MongoDB ping failed: {e}")
            return False

    def get_database(self):
        """Retourner la base de données"""
        if self._database is None:
            return self.connect()
        return self._database

    def close(self):
        """Fermer la connexion"""
        if self._client:
            self._client.close()
            logger.info("Connexion MongoDB fermée")


# Instance globale
mongo_connection = MongoDBConnection()


def get_database():
    """Helper pour obtenir la base de données"""
    return mongo_connection.get_database()


async def ping_mongo_db_server():
    """Helper pour vérifier la connexion"""
    await mongo_connection.ping()
