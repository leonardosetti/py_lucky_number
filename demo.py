#!/usr/bin/env python3
"""
Demonstração do Lucky Number
============================

Este script mostra como executar o projeto Lucky Number.
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Executa demonstração do Lucky Number."""
    print("🍀 Lucky Number - Demonstração")
    print("=" * 40)
    
    # Diretório do projeto
    project_dir = Path(__file__).parent.absolute()
    print(f"Diretório: {project_dir}")
    
    # Verificar estrutura
    required_files = [
        "pyproject.toml",
        "src/lucky_number/main.py",
        "src/lucky_number/config.py",
        "src/lucky_number/models.py",
        "src/lucky_number/services/caixa_api.py",
        "src/lucky_number/services/cache.py",
        "src/lucky_number/services/gerador.py",
        "src/lucky_number/api/routes.py",
        "static/index.html"
    ]
    
    print("\n✅ Verificando estrutura do projeto:")
    all_good = True
    for file_path in required_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (FALTANDO)")
            all_good = False
    
    if not all_good:
        print("\n❌ Estrutura incompleta!")
        return 1
    
    print("\n✅ Para executar o projeto:")
    print("   1. Instale as dependências:")
    print("      pip install fastapi uvicorn pydantic httpx")
    print("\n   2. Execute o servidor:")
    print("      python -m lucky_number.main")
    print("      OU")
    print("      uvicorn lucky_number.main:app --reload")
    print("\n   3. Acesse:")
    print("      API: http://localhost:8000/api/v1")
    print("      Web: http://localhost:8000/")
    print("      Docs: http://localhost:8000/docs")
    
    print("\n✅ Para rodar os testes:")
    print("   cd", project_dir)
    print("   PYTHONPATH=src pytest tests/ -v")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())