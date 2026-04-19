import os
import socket
from typing import Optional


def _read(name: str) -> str:
    return os.getenv(name, "").strip()


def _truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def deploy_target() -> str:
    return _read("HERMES_DEPLOY_TARGET").lower()


def is_zeabur_runtime() -> bool:
    if deploy_target() == "zeabur":
        return True
    if _read("ZEABUR_WEB_URL"):
        return True
    return False


def public_port() -> Optional[int]:
    value = _read("PORT")
    if not value:
        return None
    try:
        port = int(value)
    except ValueError:
        return None
    if 1 <= port <= 65535:
        return port
    return None


def zeabur_web_url() -> str:
    return _read("ZEABUR_WEB_URL").rstrip("/")


def zeabur_auto_api_server() -> bool:
    if not is_zeabur_runtime():
        return False
    value = _read("HERMES_ZEABUR_AUTO_API_SERVER")
    if not value:
        return True
    return _truthy(value)


def zeabur_single_service_webui() -> bool:
    """Whether Zeabur runtime should expose dashboard + API on one port."""
    if not is_zeabur_runtime():
        return False
    value = _read("HERMES_ZEABUR_SINGLE_SERVICE_WEBUI")
    if not value:
        return True
    return _truthy(value)


def is_noninteractive_runtime() -> bool:
    """Return True when the process must run without any TTY prompts.

    Triggered by explicit ``HERMES_NONINTERACTIVE=1`` or by any managed cloud
    runtime we recognise (currently Zeabur). CI-style deploys should also set
    ``HERMES_NONINTERACTIVE=1`` so setup wizards and OAuth device flows are
    skipped with a clear error instead of blocking forever on ``input()``.
    """
    explicit = _read("HERMES_NONINTERACTIVE")
    if explicit:
        return _truthy(explicit)
    if is_zeabur_runtime():
        return True
    return False


def pick_free_loopback_port() -> int:
    """Bind-and-release a loopback port to hand out a free one.

    Used to pick an internal port for the aiohttp API server in single-service
    mode so it never collides with the public ``PORT`` that the dashboard
    proxy listens on.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def internal_api_server_port() -> int:
    """Port the API server should use when running behind the dashboard proxy.

    Prefers ``HERMES_INTERNAL_API_PORT`` if explicitly set (useful for tests),
    otherwise picks a free loopback port. This is never the public PORT.
    """
    configured = _read("HERMES_INTERNAL_API_PORT")
    if configured:
        try:
            port = int(configured)
        except ValueError:
            port = 0
        if 1 <= port <= 65535:
            return port
    return pick_free_loopback_port()


def internal_dashboard_port() -> int:
    """Port the dashboard should use when fronted by the API server."""
    configured = _read("HERMES_INTERNAL_DASHBOARD_PORT")
    if configured:
        try:
            port = int(configured)
        except ValueError:
            port = 0
        if 1 <= port <= 65535:
            return port
    return pick_free_loopback_port()
