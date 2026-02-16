import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/trading_bot_ml"
)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("SUCCESS: Conexión a la base de datos establecida correctamente.")
except OperationalError as e:
    print(f"ERROR_DB_CONNECTION: Falló la conexión a la base de datos.")
    print(f"  Detalle del error: {e}")
except Exception as e:
    print(f"ERROR_UNKNOWN: Ocurrió un error inesperado durante la prueba de conexión.")
    print(f"  Detalle del error: {e}")
