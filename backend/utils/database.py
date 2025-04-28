"""Database utility module for Deepdevflow."""

import os
import yaml
from typing import Any, Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

# Import Base and models
from backend.models import Base

# Global variables
_ENGINE = None
_SESSION_FACTORY = None


def load_config() -> Dict[str, Any]:
    """Load database configuration from config file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               "config", "config.yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["database"]


def get_engine():
    """Get database engine."""
    global _ENGINE
    if _ENGINE is None:
        config = load_config()
        connection_string = config["connection_string"]
        echo = config.get("echo", False)
        _ENGINE = create_engine(connection_string, echo=echo)
    return _ENGINE


def get_session_factory():
    """Get session factory."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return _SESSION_FACTORY


def get_session() -> Session:
    """Get a new database session."""
    factory = get_session_factory()
    return factory()


def create_tables():
    """Create all tables in the database."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_tables():
    """Drop all tables from the database."""
    engine = get_engine()
    Base.metadata.drop_all(engine)


def init_db():
    """Initialize the database."""
    create_tables()
