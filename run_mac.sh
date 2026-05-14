#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${PROJECT_ROOT}/.venv"

cd "${PROJECT_ROOT}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[ERROR] ${PYTHON_BIN} not found. Install Python 3.11 first."
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "[macOS] Creating virtual environment: ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

if [ "${SKIP_INSTALL:-0}" != "1" ]; then
  echo "[macOS] Installing Python dependencies..."
  python -m pip install --upgrade pip
  python -m pip install -r requirement.txt
fi

echo "[macOS] Starting Tickets Hunter settings server..."
python src/settings.py
