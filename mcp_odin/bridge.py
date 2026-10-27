"""Puente stdio ↔ streamable-http para el MCP de Odin.

Levanta un servidor MCP local por stdio que reenvía list_tools / call_tool al
servidor MCP remoto de Odin (streamable-http) añadiendo el API token en el
header Authorization. Las tools remotas se exponen tal cual: lo que Odin ofrezca
hoy o mañana aparece sin cambiar este cliente.

Config por entorno (ningún secreto en el código):
    ODIN_MCP_URL    URL del MCP de Odin, p.ej. https://odin.macropay.mx/mcp/
    ODIN_API_TOKEN  API token del usuario (odin_...), creado en la UI de Odin.
"""

from __future__ import annotations

import os
import sys

import anyio
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.lowlevel import Server
import mcp.server.stdio


def _is_local(host: str) -> bool:
    return host in ("localhost", "127.0.0.1", "::1") or host.endswith(".local")


def _config() -> tuple[str, str]:
    from urllib.parse import urlparse

    url = os.environ.get("ODIN_MCP_URL", "").strip()
    token = os.environ.get("ODIN_API_TOKEN", "").strip()
    if not url:
        _die("Falta ODIN_MCP_URL (p.ej. https://odin.macropay.mx/mcp/).")
    if not token:
        _die("Falta ODIN_API_TOKEN (crea un token en Odin → Administración → API Tokens).")
    if not token.startswith("odin_"):
        _die("ODIN_API_TOKEN no parece un token de Odin (debe empezar con 'odin_').")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        _die("ODIN_MCP_URL debe ser http(s).")
    # Seguridad: el token viaja en el header. Fuera de localhost se EXIGE HTTPS
    # para no enviarlo en claro. Se puede forzar con ODIN_ALLOW_INSECURE=1 (solo
    # para labs internos; desaconsejado).
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "http" and not _is_local(host):
        if os.environ.get("ODIN_ALLOW_INSECURE", "").strip() not in ("1", "true", "yes"):
            _die(
                "ODIN_MCP_URL usa HTTP hacia un host remoto: el token viajaría en "
                "claro. Usa HTTPS, o pon ODIN_ALLOW_INSECURE=1 bajo tu propio riesgo."
            )

    if not url.endswith("/"):
        url += "/"  # el endpoint MCP vive en /mcp/
    return url, token


def _die(msg: str) -> None:
    print(f"[mcp-odin] {msg}", file=sys.stderr)
    sys.exit(1)


async def _run() -> None:
    url, token = _config()
    headers = {"Authorization": f"Bearer {token}"}

    # Conexión persistente al MCP remoto de Odin.
    async with streamablehttp_client(url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as remote:
            await remote.initialize()

            server = Server("odin")

            @server.list_tools()
            async def _list_tools() -> list[types.Tool]:
                resp = await remote.list_tools()
                return resp.tools

            @server.call_tool()
            async def _call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
                result = await remote.call_tool(name, arguments or {})
                return result.content

            # Servir por stdio al cliente local (Kiro/Claude/Cursor).
            opts = server.create_initialization_options()
            async with mcp.server.stdio.stdio_server() as (r, w):
                await server.run(r, w, opts)


def _redact(text: str) -> str:
    """Nunca dejar que un token aparezca en logs/mensajes de error."""
    tok = os.environ.get("ODIN_API_TOKEN", "").strip()
    if tok and tok in text:
        text = text.replace(tok, "odin_***redacted***")
    return text


def main() -> None:
    """Entry point: `mcp-odin`."""
    try:
        anyio.run(_run)
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # fallo de conexión/auth → mensaje claro, no stacktrace
        _die(_redact(f"No se pudo conectar al MCP de Odin: {exc}"))


if __name__ == "__main__":
    main()
