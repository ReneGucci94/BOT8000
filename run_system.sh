#!/bin/bash
echo "Starting BOT8000 V3 System..."

# Asegurar directorios
mkdir -p data/raw data/models src/api/static

# Check dependencies
echo "Checking dependencies..."
# Simple check
python3 -c "import fastapi, uvicorn, sklearn, pandas, numpy, sqlalchemy, psycopg2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Faltan dependencias. Instalar con pip..."
    # No auto-install in script, let user do it
fi

# Iniciar Uvicorn
echo "Launching API Server on http://localhost:8000"
python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
