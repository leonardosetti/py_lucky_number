#!/usr/bin/env python3
"""
Script para executar o Lucky Number facilmente.
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path para importar módulos
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root / "src"))

def main():
    """Executa o servidor Lucky Number."""
    print("🚀 Iniciando Lucky Number...")
    print("=" * 40)
    
    try:
        # Importar e executar a aplicação
        from lucky_number.main import app
        import uvicorn
        
        print("🎮 Servidor disponível em:")
        print("   API: http://localhost:8000/api/v1")
        print("   Web: http://localhost:8000/")
        print("   Docs: http://localhost:8000/docs")
        print("   (Pressione Ctrl+C para parar)")
        print()
        
        uvicorn.run(
            "lucky_number.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())