# backend/db/session.py

import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Handle PyInstaller bundled path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = os.path.dirname(sys.executable)
else:
    # Running as script
    base_path = os.path.dirname(os.path.dirname(__file__))

def get_database_url():
    """Get database URL from db_config.json or default to SQLite"""
    config_file = os.path.join(base_path, "db_config.json")
    
    # Try to read from db_config.json (created by Connection Manager)
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                db_type = config.get("type", "sqlite")
                
                if db_type == "postgresql" and config.get("config"):
                    cfg = config["config"]
                    host = cfg.get("host", "localhost")
                    port = cfg.get("port", 5432)
                    database = cfg.get("database", "")
                    username = cfg.get("username", "")
                    password = cfg.get("password", "")
                    if host and database and username:
                        return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        except Exception as e:
            print(f"Warning: Could not read db_config.json: {e}")
    
    # Default to SQLite (no configuration needed)
    db_file = os.path.join(base_path, "accessioning_app.db")
    return f"sqlite:///{db_file}"

DATABASE_URL = get_database_url()

def create_database_engine(database_url=None):
    """Create a new database engine with the given URL"""
    url = database_url or DATABASE_URL
    
    # Configure engine based on database type
    if url.startswith('sqlite'):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},  # Required for SQLite
        )
    else:
        return create_engine(
            url,
            pool_pre_ping=True,   # Check connections before using
            pool_size=10,         # Increase from default 5
            max_overflow=20,      # Increase from default 10
            pool_timeout=60,      # Give more time for operations to complete
        )

# Create initial engine
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initialize_database():
    """Initialize or reinitialize the database connection"""
    global engine, SessionLocal, DATABASE_URL
    
    # Reload DATABASE_URL from config file
    DATABASE_URL = get_database_url()
    
    # Close existing connections if any
    if engine:
        engine.dispose()
    
    # Create new engine and session
    engine = create_database_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print(f"Database reinitialized: {DATABASE_URL}")
    return engine, SessionLocal

# Check database connection in db/session.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        db.close()
