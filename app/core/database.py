import logging

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


def _get_mongodb_uri() -> str:
    uri = (settings.MONGODB_URI or "").strip()
    # Only fall back to localhost when no URI or placeholder credentials are present.
    if not uri or "YOUR_USERNAME" in uri or "YOUR_PASSWORD" in uri:
        return "mongodb://127.0.0.1:27017"
    return uri


async def connect_to_mongo() -> None:
    logger.info("Connecting to MongoDB...")

    try:
        mongodb.client = AsyncIOMotorClient(
            _get_mongodb_uri(),
            tls=True,
            tlsCAFile=certifi.where(),
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=20000,
        )

        mongodb.database = mongodb.client[settings.MONGODB_DB_NAME]

        if settings.MONGODB_CONNECT_ON_STARTUP:
            await mongodb.client.admin.command("ping")
            logger.info(
                "MongoDB connection established: database='%s'",
                settings.MONGODB_DB_NAME,
            )
        else:
            logger.info(
                "MongoDB client created without startup ping; database will connect lazily."
            )
    except Exception as exc:  # pragma: no cover - defensive startup handling
        mongodb.client = None
        mongodb.database = None
        logger.warning("MongoDB connection unavailable during startup: %s", exc)
        logger.warning("Continuing without a live MongoDB connection; database-backed routes will fail until the database is reachable.")


async def close_mongo_connection() -> None:
    if mongodb.client is not None:
        mongodb.client.close()
        mongodb.client = None
        mongodb.database = None
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.database is None:
        raise RuntimeError(
            "Database is not initialized. connect_to_mongo() must run during app startup."
        )
    return mongodb.database