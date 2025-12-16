from psycopg_pool import ConnectionPool #type: ignore
import os 

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "8501"),
    "dbname": os.getenv("DB_NAME", "artatlas"),
    "user": os.getenv("DB_USER", "artuser"),
    "password": os.getenv("DB_PASSWORD", "artpass"),
}

DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
    f"/{DATABASE_CONFIG['dbname']}"
)

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    timeout=30,
    max_idle=300,
    kwargs={
        "autocommit": False,
        "prepare_threshold": 0,  # good for dynamic queries / vector ops
    },
)

def get_connection():
    """
    Acquire a connection from the pool.
    Use as context manager.
    """
    return pool.connection()

def close_pool():
    pool.close()