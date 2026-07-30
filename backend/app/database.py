"""
database.py

Handles all database connectivity for the Autonomous Context-Bridging
Knowledge Agent backend.

Responsibilities:
    - Load environment variables from .env
    - Create the SQLAlchemy engine (PostgreSQL via psycopg)
    - Create the SessionLocal factory
    - Create the declarative Base used by all ORM models
    - Expose a get_db() dependency for FastAPI routes
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

# ----------------------------------------------------------------------
# Load environment variables from .env
# ----------------------------------------------------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "knowledge_agent_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ----------------------------------------------------------------------
# Build the PostgreSQL connection URL (psycopg driver)
# ----------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# ----------------------------------------------------------------------
# SQLAlchemy engine
# ----------------------------------------------------------------------
# pool_pre_ping avoids "server closed the connection unexpectedly" errors
# for long-lived connections.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# ----------------------------------------------------------------------
# Session factory
# ----------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# ----------------------------------------------------------------------
# Declarative base for all ORM models
# ----------------------------------------------------------------------
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and guarantees
    it is closed after the request completes, even if an exception
    is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
