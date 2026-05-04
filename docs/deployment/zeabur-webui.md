# Zeabur WebUI deployment

Hermes can run the bundled agent and Hermes WebUI from one Dockerfile service. The
container exposes the WebUI on port `8787` and keeps all mutable data under one
persistent volume at `/opt/data`.

## Zeabur service

Create a Zeabur Git service from this repository and use the existing
`Dockerfile`.

Configure:

- **Port:** `8787`
- **Volume:** mount persistent storage at `/opt/data`
- **Start command:** `webui`
  - Alternative: leave the command empty and set `HERMES_WEBUI=1`.

Do not mount volumes over `/opt/hermes` or `/opt/hermes-webui`. Those paths are
image source directories: `/opt/hermes` contains the agent source and virtualenv,
and `/opt/hermes-webui` contains the WebUI source fetched during the Docker
build. Mounting over either path hides the code the WebUI imports at runtime.

## Required environment

Set the same provider credentials you would use for a normal Hermes container,
for example API keys used by your selected model provider. Set
`HERMES_WEBUI_PASSWORD` before exposing a public Zeabur domain. The Docker WebUI
entrypoint refuses to start on non-loopback hosts unless this password is set.

Useful runtime variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `HERMES_WEBUI_PASSWORD` | unset | Required before exposing WebUI on a public Zeabur domain. |
| `HERMES_WEBUI` | unset | When `1`, `true`, or `yes` and no command is supplied, starts WebUI. |
| `HERMES_WEBUI_HOST` | `0.0.0.0` | Bind address inside the container. |
| `HERMES_WEBUI_PORT` | unset | Optional explicit WebUI port. If unset, the entrypoint honors Zeabur `PORT`, then falls back to `8787`. |
| `HERMES_HOME` | `/opt/data` | Hermes state, config, logs, skills, and profiles. |
| `HERMES_WEBUI_STATE_DIR` | `/opt/data/webui` | WebUI state directory. |
| `HERMES_WEBUI_DEFAULT_WORKSPACE` | `/opt/data/workspace` | Default workspace shown to the WebUI. |
| `HERMES_WEBUI_AGENT_DIR` | `/opt/hermes` | Local agent source imported by WebUI. |
| `HERMES_WEBUI_PYTHON` | `/opt/hermes/.venv/bin/python` | Python interpreter with agent and WebUI dependencies. |

## Build args

The Docker build fetches Hermes WebUI from a pinned repository and ref instead
of vendoring it into this repository.

Defaults:

```text
HERMES_WEBUI_REPO=https://github.com/Youzini-afk/hermes-webui.git
HERMES_WEBUI_REF=9986d2fd30810045d0d02abff3e264c0be802bae
```

Override these build args in Zeabur only when intentionally testing or rolling
forward the WebUI. Prefer pinning a commit SHA for reproducible deploys.

## Update workflow

- **Update Hermes agent:** deploy a newer commit of this repository. The same
  Dockerfile still builds the agent into `/opt/hermes` and keeps runtime data in
  `/opt/data`.
- **Update Hermes WebUI:** change `HERMES_WEBUI_REF` to a reviewed WebUI commit
  SHA, rebuild, and redeploy. If using a fork, also change `HERMES_WEBUI_REPO`.
  WebUI dependency changes are installed into the same Python environment as the
  agent, so smoke-test both `webui` and normal `hermes` modes after bumping.
- **Roll back:** restore the previous repository commit and/or WebUI ref and
  redeploy. Persistent user data remains under `/opt/data`.

## Why one service

The current WebUI architecture imports `run_agent.AIAgent` directly from a local
Hermes checkout and launches it with the local Python interpreter. Running WebUI
as a separate Zeabur service would require a second synchronized copy of the
agent source, duplicated dependencies, and cross-service filesystem assumptions
that Zeabur services do not provide. A single Dockerfile service keeps the WebUI,
agent source, virtualenv, and persistent state in one container, which matches the
current architecture and exposes only one public port.
