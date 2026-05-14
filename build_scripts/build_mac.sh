#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${PROJECT_ROOT}/.venv"
RELEASE_DIR="${PROJECT_ROOT}/dist/tickets_hunter_macos"
ZIP_NAME="tickets_hunter_macos_$(date +%Y%m%d_%H%M%S).zip"

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

echo "[macOS] Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirement.txt pyinstaller

echo "[macOS] Building nodriver_tixcraft..."
python -m PyInstaller build_scripts/nodriver_tixcraft.spec --noconfirm --clean

echo "[macOS] Building settings..."
python -m PyInstaller build_scripts/settings.spec --noconfirm --clean

echo "[macOS] Assembling release folder..."
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}/_internal"

cp "${PROJECT_ROOT}/dist/nodriver_tixcraft/nodriver_tixcraft" "${RELEASE_DIR}/"
cp "${PROJECT_ROOT}/dist/settings/settings" "${RELEASE_DIR}/"
ditto "${PROJECT_ROOT}/dist/nodriver_tixcraft/_internal" "${RELEASE_DIR}/_internal"
ditto "${PROJECT_ROOT}/dist/settings/_internal" "${RELEASE_DIR}/_internal"
ditto "${PROJECT_ROOT}/src/assets" "${RELEASE_DIR}/assets"
ditto "${PROJECT_ROOT}/src/www" "${RELEASE_DIR}/www"

if [ -f "${PROJECT_ROOT}/README.md" ]; then
  cp "${PROJECT_ROOT}/README.md" "${RELEASE_DIR}/"
fi

if [ -f "${PROJECT_ROOT}/CHANGELOG.md" ]; then
  cp "${PROJECT_ROOT}/CHANGELOG.md" "${RELEASE_DIR}/"
fi

chmod +x "${RELEASE_DIR}/settings" "${RELEASE_DIR}/nodriver_tixcraft"

mkdir -p "${PROJECT_ROOT}/dist/release"
ditto -c -k --sequesterRsrc --keepParent "${RELEASE_DIR}" "${PROJECT_ROOT}/dist/release/${ZIP_NAME}"

echo "[macOS] Build complete:"
echo "  Folder: ${RELEASE_DIR}"
echo "  ZIP:    ${PROJECT_ROOT}/dist/release/${ZIP_NAME}"
echo ""
echo "Run with:"
echo "  cd ${RELEASE_DIR}"
echo "  ./settings"
