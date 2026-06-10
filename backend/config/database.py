"""
config/database.py
──────────────────
Manages the MongoDB Atlas connection lifecycle for LifeReel AI.

Responsibilities
----------------
- Initialise a single MongoClient from the MONGO_URI environment variable.
- Expose a `verify_connection()` coroutine that fires a ping command so the
  FastAPI startup event can confirm Atlas reachability before the first request
  is ever accepted.
- Export the target database and collection as module-level singletons so every
  route and service can import them without re-creating the client.
"""

import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ConnectionFailure, ServerSelectionTimeoutError

from config.settings import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Client initialisation
# ──────────────────────────────────────────────────────────────────────────────

def _create_client() -> MongoClient:
    """
    Build and return a MongoClient.

    serverSelectionTimeoutMS is intentionally short (5 s) so a misconfigured
    MONGO_URI surfaces immediately at startup rather than blocking the first
    real request for 30 seconds.
    """
    try:
        client: MongoClient = MongoClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5_000,
        )
        logger.info("MongoClient created successfully.")
        return client
    except ConfigurationError as exc:
        logger.critical(
            "MONGO_URI is malformed – cannot create MongoClient.",
            extra={"error": str(exc)},
        )
        raise


client: MongoClient = _create_client()

# ──────────────────────────────────────────────────────────────────────────────
# Database & collection exports
# ──────────────────────────────────────────────────────────────────────────────

db: Database = client["LifeReelAI_DB"]
journal_entries: Collection = db["journal_entries"]
users: Collection = db["users"]

# ──────────────────────────────────────────────────────────────────────────────
# Startup verification
# ──────────────────────────────────────────────────────────────────────────────

async def verify_connection() -> None:
    """
    Ping MongoDB Atlas to confirm the connection is live.

    Called once from FastAPI's `lifespan` startup hook.  Raises
    `ConnectionFailure` if the cluster is unreachable so the process exits
    with a clear error rather than silently accepting requests that will all
    fail at the database layer.
    """
    try:
        client.admin.command("ping")
        logger.info(
            "MongoDB Atlas ping succeeded – database connection verified.",
            extra={"database": "LifeReelAI_DB"},
        )
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.critical(
            "MongoDB Atlas ping FAILED – check MONGO_URI and network access.",
            extra={"error": str(exc)},
        )
        raise
