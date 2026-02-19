from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import Optional
import os
import sys
import json
from pathlib import Path

from db.session import get_db, initialize_database

router = APIRouter()

class DatabaseConfig(BaseModel):
    host: str
    port: str
    database: str
    username: str
    password: str

class ConnectionRequest(BaseModel):
    type: str  # 'sqlite' or 'postgresql'
    config: Optional[DatabaseConfig] = None

# Get config path (next to executable in production)
if getattr(sys, 'frozen', False):
    CONFIG_DIR = Path(sys.executable).parent
else:
    CONFIG_DIR = Path(__file__).parent.parent

CONFIG_FILE = CONFIG_DIR / 'db_config.json'

def get_current_config():
    """Read current database configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    # Default SQLite config
    return {
        'type': 'sqlite',
        'config': {
            'host': '',
            'port': '5432',
            'database': 'accessioning_app',
            'username': '',
            'password': ''
        }
    }

def save_config(config_data: dict):
    """Save database configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

@router.get("/database/connection")
async def get_connection():
    """Get current database connection configuration"""
    config = get_current_config()
    # Don't send password back
    if config.get('config'):
        config['config']['password'] = ''
    return config

@router.post("/database/test")
async def test_connection(request: ConnectionRequest):
    """Test database connection without saving"""
    if request.type == 'sqlite':
        # SQLite is always available
        return {"success": True, "message": "SQLite connection available"}
    
    elif request.type == 'postgresql':
        if not request.config:
            raise HTTPException(status_code=400, detail="PostgreSQL requires configuration")
        
        try:
            # Build connection string
            conn_str = f"postgresql+psycopg2://{request.config.username}:{request.config.password}@{request.config.host}:{request.config.port}/{request.config.database}"
            
            # Try to connect
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return {
                "success": True, 
                "message": f"Successfully connected to PostgreSQL database '{request.config.database}'"
            }
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages
            if "does not exist" in error_msg:
                detail = f"Database '{request.config.database}' does not exist. Please create it first:\n\nCREATE DATABASE {request.config.database};"
            elif "authentication failed" in error_msg or "password authentication failed" in error_msg:
                detail = "Authentication failed. Please check your username and password."
            elif "Connection refused" in error_msg or "could not connect" in error_msg:
                detail = f"Cannot connect to PostgreSQL server at {request.config.host}:{request.config.port}. Is the server running?"
            else:
                detail = f"Connection failed: {error_msg}"
            
            raise HTTPException(status_code=400, detail=detail)
    else:
        raise HTTPException(status_code=400, detail="Invalid database type")

@router.post("/database/connection")
async def save_connection(request: ConnectionRequest):
    """Save database connection configuration and reload"""
    config_data = {
        'type': request.type
    }
    
    if request.type == 'postgresql':
        if not request.config:
            raise HTTPException(status_code=400, detail="PostgreSQL requires configuration")
        
        config_data['config'] = {
            'host': request.config.host,
            'port': request.config.port,
            'database': request.config.database,
            'username': request.config.username,
            'password': request.config.password
        }
    else:
        # SQLite - empty config
        config_data['config'] = {}
    
    try:
        save_config(config_data)
        
        # Hot reload the database connection
        from db.models import Base
        
        engine, SessionLocal = initialize_database()
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        return {
            "success": True, 
            "message": f"Successfully switched to {request.type} database!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save configuration: {str(e)}"
        )
