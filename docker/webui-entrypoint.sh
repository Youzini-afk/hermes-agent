#!/bin/bash
set -e

HERMES_WEBUI_AGENT_DIR="${HERMES_WEBUI_AGENT_DIR:-/opt/hermes}"
HERMES_WEBUI_PYTHON="${HERMES_WEBUI_PYTHON:-/opt/hermes/.venv/bin/python}"
HERMES_WEBUI_STATE_DIR="${HERMES_WEBUI_STATE_DIR:-/opt/data/webui}"
HERMES_WEBUI_DEFAULT_WORKSPACE="${HERMES_WEBUI_DEFAULT_WORKSPACE:-/opt/data/workspace}"
HERMES_WEBUI_HOST="${HERMES_WEBUI_HOST:-0.0.0.0}"
HERMES_WEBUI_PORT="${HERMES_WEBUI_PORT:-${PORT:-8787}}"

export HERMES_WEBUI_AGENT_DIR
export HERMES_WEBUI_PYTHON
export HERMES_WEBUI_STATE_DIR
export HERMES_WEBUI_DEFAULT_WORKSPACE
export HERMES_WEBUI_HOST
export HERMES_WEBUI_PORT

case "$HERMES_WEBUI_HOST" in
    127.0.0.1|localhost|::1)
        ;;
    *)
        if [ -z "${HERMES_WEBUI_PASSWORD:-}" ]; then
            echo "HERMES_WEBUI_PASSWORD is required when WebUI binds to $HERMES_WEBUI_HOST." >&2
            echo "Set HERMES_WEBUI_PASSWORD before exposing Hermes WebUI on Zeabur." >&2
            exit 1
        fi
        ;;
esac

mkdir -p "$HERMES_WEBUI_STATE_DIR" "$HERMES_WEBUI_DEFAULT_WORKSPACE"

cd /opt/hermes-webui
exec "$HERMES_WEBUI_PYTHON" server.py "$@"
