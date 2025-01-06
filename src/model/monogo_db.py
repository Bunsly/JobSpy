from pymongo import MongoClient
from pymongo.synchronous.database import Database

from config.settings import settings
from scrapers.utils import create_logger


class MongoDB:
    def __init__(self):
        logger = create_logger("Mongo Client")
        mongo_uri = settings.mongo_uri
        if not mongo_uri:
            logger.error("MONGO_URI environment variable is not set")
            raise ValueError("MONGO_URI environment variable is not set")
        client = MongoClient(mongo_uri)
        database_name = settings.mongo_db_name
        if not database_name:
            logger.error("MONGO_DB_NAME environment variable is not set")
            raise ValueError(
                "MONGO_DB_NAME environment variable is not set")

        self._db: Database = client[database_name]
        logger.info("Succeed connect to MongoDB")

    def get_collection(self,
                       name: str,
                       codec_options=None,
                       read_preference=None,
                       write_concern=None,
                       read_concern=None):
        return self._db.get_collection(name,
                                       codec_options,
                                       read_preference,
                                       write_concern,
                                       read_concern)


mongo_client = MongoDB()
