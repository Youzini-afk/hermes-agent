from unittest.mock import patch

from hermes_cli.web_server import start_server, start_server_background


def test_start_server_uses_platform_port_and_disables_browser_on_zeabur(monkeypatch):
    monkeypatch.setenv("HERMES_DEPLOY_TARGET", "zeabur")
    monkeypatch.setenv("PORT", "4321")
    with patch("uvicorn.run") as mock_run, patch("webbrowser.open") as mock_open:
        start_server(open_browser=True)

    _, kwargs = mock_run.call_args
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 4321
    mock_open.assert_not_called()


def test_start_server_keeps_explicit_port_on_zeabur(monkeypatch):
    monkeypatch.setenv("HERMES_DEPLOY_TARGET", "zeabur")
    monkeypatch.setenv("PORT", "4321")
    with patch("uvicorn.run") as mock_run:
        start_server(port=9999, open_browser=False)

    _, kwargs = mock_run.call_args
    assert kwargs["port"] == 9999


def test_start_server_background_can_skip_runtime_port_remap(monkeypatch):
    monkeypatch.setenv("HERMES_DEPLOY_TARGET", "zeabur")
    monkeypatch.setenv("PORT", "4321")

    captured = {}

    class DummyConfig:
        def __init__(self, app, host, port, log_level):
            captured["host"] = host
            captured["port"] = port

    class DummyServer:
        def __init__(self, config):
            self.started = True
            self.should_exit = False

        def run(self):
            return None

    class DummyThread:
        def __init__(self, *args, **kwargs):
            self._alive = True

        def start(self):
            return None

        def is_alive(self):
            return self._alive

        def join(self, timeout=None):
            self._alive = False

    with (
        patch("uvicorn.Config", DummyConfig),
        patch("uvicorn.Server", DummyServer),
        patch("hermes_cli.web_server.threading.Thread", DummyThread),
    ):
        handle = start_server_background(
            host="127.0.0.1",
            port=9119,
            open_browser=False,
            allow_public=False,
            respect_runtime_defaults=False,
        )

    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9119
    assert handle.port == 9119
