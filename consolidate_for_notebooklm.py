#!/usr/bin/env python3
"""
Consolidador de código para Notebook LM
Convierte 1,462 archivos Python en ~30 fuentes de texto
"""

import os
import glob
from pathlib import Path

# Configuración
SOURCE_DIR = "/Users/feux/Desktop/BOT8000"
OUTPUT_DIR = "/Users/feux/Desktop/BOT8000/notebooklm-sources"
MAX_WORDS_PER_FILE = 450000  # Dejar margen al límite de 500K

# Exclusiones
EXCLUDE_PATTERNS = [
    "**/__pycache__/**",
    "**/.git/**",
    "**/venv/**",
    "**/.venv/**",
    "**/node_modules/**",
    "**/.pytest_cache/**",
    "**/tests/**",
    "**/test_*.py",
    "**/*_test.py",
]

def count_words(text):
    """Cuenta palabras aproximadas"""
    return len(text.split())

def should_include(filepath):
    """Verifica si el archivo debe incluirse"""
    path = Path(filepath)
    
    # Solo archivos Python
    if not path.suffix == '.py':
        return False
    
    # Verificar exclusiones
    for pattern in EXCLUDE_PATTERNS:
        if path.match(pattern):
            return False
    
    return True

def consolidate_files():
    """Consolida archivos Python en chunks"""
    
    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Encontrar todos los archivos Python
    all_py_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv', 'node_modules', '.pytest_cache', 'tests']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if should_include(filepath):
                    all_py_files.append(filepath)
    
    print(f"📁 Encontrados {len(all_py_files)} archivos Python")
    
    # Ordenar por directorio para mantener estructura lógica
    all_py_files.sort()
    
    # Consolidar en chunks
    current_chunk = []
    current_words = 0
    chunk_number = 1
    
    for filepath in all_py_files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Crear header con info del archivo
            rel_path = os.path.relpath(filepath, SOURCE_DIR)
            header = f"\n{'='*80}\n# FILE: {rel_path}\n{'='*80}\n\n"
            
            file_content = header + content
            file_words = count_words(file_content)
            
            # Si añadir este archivo excede el límite, guardar chunk actual
            if current_words + file_words > MAX_WORDS_PER_FILE and current_chunk:
                save_chunk(current_chunk, chunk_number)
                chunk_number += 1
                current_chunk = []
                current_words = 0
            
            current_chunk.append(file_content)
            current_words += file_words
            
        except Exception as e:
            print(f"⚠️ Error leyendo {filepath}: {e}")
    
    # Guardar último chunk
    if current_chunk:
        save_chunk(current_chunk, chunk_number)
    
    print(f"✅ Consolidación completa: {chunk_number} archivos en {OUTPUT_DIR}/")
    
    # Crear índice
    create_index(all_py_files, chunk_number)

def save_chunk(contents, number):
    """Guarda un chunk de archivos"""
    output_file = os.path.join(OUTPUT_DIR, f"bot8000-code-chunk-{number:02d}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# BOT8000 Trading Bot - Source Code Chunk {number}\n")
        f.write(f"# Generated for Notebook LM ingestion\n")
        f.write(f"# Total files in this chunk: {len(contents)}\n")
        f.write("="*80 + "\n\n")
        f.write("\n".join(contents))
    
    word_count = count_words("\n".join(contents))
    print(f"  💾 Chunk {number}: {len(contents)} archivos, ~{word_count:,} palabras")

def create_index(all_files, total_chunks):
    """Crea archivo índice"""
    index_file = os.path.join(OUTPUT_DIR, "00_INDEX.txt")
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("# BOT8000 Trading Bot - Notebook LM Source Index\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total Python files: {len(all_files)}\n")
        f.write(f"Consolidated into: {total_chunks} chunks\n")
        f.write(f"Max words per chunk: {MAX_WORDS_PER_FILE:,}\n\n")
        
        f.write("## Directory Structure:\n\n")
        
        # Agrupar por directorio
        dirs = {}
        for filepath in all_files:
            rel_path = os.path.relpath(filepath, SOURCE_DIR)
            dir_name = os.path.dirname(rel_path) or "root"
            if dir_name not in dirs:
                dirs[dir_name] = []
            dirs[dir_name].append(os.path.basename(filepath))
        
        for dir_name in sorted(dirs.keys()):
            f.write(f"\n### {dir_name}/\n")
            for filename in sorted(dirs[dir_name])[:10]:  # Limitar a 10 por directorio
                f.write(f"  - {filename}\n")
            if len(dirs[dir_name]) > 10:
                f.write(f"  ... and {len(dirs[dir_name]) - 10} more files\n")
        
        f.write("\n\n## Key Components:\n\n")
        f.write("- src/agents/ - Trading agents (Trend Hunter, Mean Reversion, etc.)\n")
        f.write("- src/core/ - Core logic (Orchestrator, Market State)\n")
        f.write("- src/execution/ - Order execution and risk management\n")
        f.write("- src/alphas/ - Alpha signal generators\n")
        f.write("- src/strategy/ - Trading strategies\n")
        f.write("- src/database/ - Database models and connection\n")
        f.write("- src/optimization/ - Genetic Algorithm and WFO\n")
        f.write("- src/api/ - FastAPI REST API\n")
        f.write("- src/ml/ - Machine learning components\n")
    
    print(f"📑 Índice creado: {index_file}")

if __name__ == "__main__":
    consolidate_files()
