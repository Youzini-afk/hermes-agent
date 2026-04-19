import os
from unittest.mock import patch

from gateway.config import GatewayConfig, Platform, _apply_env_overrides
from hermes_cli.runtime_env import zeabur_single_service_webui


def test_zeabur_runtime_auto_enables_api_server():
    config = GatewayConfig()
    env = {
        "HERMES_DEPLOY_TARGET": "zeabur",
        "PORT": "8080",
        "API_SERVER_KEY": "sk-zeabur",
        "ZEABUR_WEB_URL": "https://hermes.example",
    }
    with patch.dict(os.environ, env, clear=True):
        _apply_env_overrides(config)

    api_config = config.platforms[Platform.API_SERVER]
    assert api_config.enabled is True
    assert api_config.extra["host"] == "0.0.0.0"
    assert api_config.extra["port"] == 8080
    assert api_config.extra["key"] == "sk-zeabur"
    assert api_config.extra["cors_origins"] == ["https://hermes.example"]


def test_explicit_api_server_env_overrides_zeabur_runtime_defaults():
    config = GatewayConfig()
    env = {
        "HERMES_DEPLOY_TARGET": "zeabur",
        "PORT": "8080",
        "API_SERVER_ENABLED": "true",
        "API_SERVER_HOST": "10.0.0.1",
        "API_SERVER_PORT": "7777",
        "API_SERVER_CORS_ORIGINS": "https://app.example",
    }
    with patch.dict(os.environ, env, clear=True):
        _apply_env_overrides(config)

    api_config = config.platforms[Platform.API_SERVER]
    assert api_config.extra["host"] == "10.0.0.1"
    assert api_config.extra["port"] == 7777
    assert api_config.extra["cors_origins"] == ["https://app.example"]


def test_zeabur_auto_api_server_can_be_disabled():
    config = GatewayConfig()
    env = {
        "HERMES_DEPLOY_TARGET": "zeabur",
        "PORT": "8080",
        "HERMES_ZEABUR_AUTO_API_SERVER": "false",
    }
    with patch.dict(os.environ, env, clear=True):
        _apply_env_overrides(config)

    assert Platform.API_SERVER not in config.platforms


def test_zeabur_single_service_webui_enabled_by_default():
    with patch.dict(os.environ, {"HERMES_DEPLOY_TARGET": "zeabur"}, clear=True):
        assert zeabur_single_service_webui() is True


def test_zeabur_single_service_webui_can_be_disabled():
    env = {
        "HERMES_DEPLOY_TARGET": "zeabur",
        "HERMES_ZEABUR_SINGLE_SERVICE_WEBUI": "false",
    }
    with patch.dict(os.environ, env, clear=True):
        assert zeabur_single_service_webui() is False
