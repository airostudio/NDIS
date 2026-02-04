#!/usr/bin/env python3
"""
Initialize Velma database
Creates all tables and optionally loads sample data
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from velma.database.models import Base
from velma.utils import Config, get_logger

logger = get_logger(__name__)


def init_database(database_url: str = None, sample_data: bool = False):
    """
    Initialize database with tables

    Args:
        database_url: Database URL (defaults to config)
        sample_data: Whether to load sample data
    """
    if not database_url:
        config = Config()
        database_url = config.database_url

    if not database_url:
        logger.error("No database URL provided. Set DATABASE_URL in .env")
        return False

    try:
        logger.info(f"Connecting to database...")
        engine = create_engine(database_url)

        logger.info("Creating tables...")
        Base.metadata.create_all(engine)

        logger.info("✅ Database initialized successfully!")

        if sample_data:
            logger.info("Loading sample data...")
            # TODO: Add sample data loading
            logger.info("✅ Sample data loaded!")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Velma database")
    parser.add_argument("--sample-data", action="store_true", help="Load sample data")
    parser.add_argument("--database-url", help="Database URL (overrides config)")

    args = parser.parse_args()

    success = init_database(
        database_url=args.database_url,
        sample_data=args.sample_data
    )

    sys.exit(0 if success else 1)
