#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  build.sh  –  Empacota o App Comex como executável standalone
#
#  Uso:
#    chmod +x build.sh
#    ./build.sh
#
#  Pré-requisitos:
#    Python 3.10+ instalado e no PATH
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "============================================"
echo "  App Comex – Build de Executável"
echo "============================================"

# 1. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Dependências
pip install --upgrade pip
pip install flet numpy pyinstaller

# 3. Empacota com flet pack (usa PyInstaller internamente)
#    --name        : nome do executável
#    --product-name: nome exibido no SO
flet pack main.py \
    --name "AppComex" \
    --product-name "App Comex – Exportação" \
    --add-data "*.py:." \
    || true

# Fallback: PyInstaller direto (caso flet pack não esteja disponível na versão)
if [ ! -f "dist/AppComex" ] && [ ! -f "dist/AppComex.exe" ]; then
  echo ""
  echo "[!] flet pack não gerou executável – usando PyInstaller direto..."
  pyinstaller --onefile --windowed \
    --name "AppComex" \
    --hidden-import flet \
    --hidden-import flet.app \
    --hidden-import numpy \
    --hidden-import pandas \
    main.py
fi

deactivate

echo ""
echo "✅  Executável gerado em: dist/AppComex"
echo "============================================"
