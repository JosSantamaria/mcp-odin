# mcp-odin

Cliente puente para el **MCP de Odin**. Conecta tu asistente (Kiro, Claude
Desktop, Cursor, etc.) con el inventario de Odin (EC2, DNS, Checkpoint/Entra…)
de solo lectura, usando tu **API token** personal.

El MCP de Odin vive en el backend de Odin (self-hosted). Este paquete solo es el
**puente**: traduce stdio (lo que hablan los clientes locales) al transporte
streamable-http del servidor remoto, añadiendo tu token. **No contiene secretos**:
la URL y el token se leen de variables de entorno.

## Requisitos

- Python 3.10+ y [uv](https://docs.astral.sh/uv/) (o pip).
- Un **API token de Odin**: entra a Odin → **Administración → API Tokens** →
  *Nuevo token*, elige el preset **Solo lectura** y las apps que necesites
  (p.ej. `Inventario AWS`, `Checkpoint/Entra`). Copia el `odin_...` (se muestra
  una sola vez).

## Instalación

```bash
# Con uv (recomendado, sin instalar nada permanente):
uvx --from git+https://github.com/JosSantamaria/mcp-odin mcp-odin

# O instalación con pip:
pip install git+https://github.com/JosSantamaria/mcp-odin
```

## Configuración

Dos variables de entorno (cada usuario las suyas):

```bash
# Sustituye por la URL de tu instancia de Odin (pídela a tu admin).
export ODIN_MCP_URL="https://odin.<instance>.<domain>.tld/mcp/"
export ODIN_API_TOKEN="odin_xxxxxxxx..."   # tu token personal
```

## Registrar en tu asistente

### Kiro / Claude Desktop / Cursor (config MCP)

En el `mcp.json` del cliente (en Kiro: `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "odin": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JosSantamaria/mcp-odin", "mcp-odin"],
      "env": {
        "ODIN_MCP_URL": "https://odin.<instance>.<domain>.tld/mcp/",
        "ODIN_API_TOKEN": "odin_xxxxxxxx..."
      }
    }
  }
}
```

Cada persona del equipo pone **su propio** `ODIN_API_TOKEN`; el acceso que
tendrá (apps y permisos) es el que el admin le asignó a su usuario en Odin.

## Herramientas disponibles (solo lectura)

Las expone el servidor de Odin y se reenvían tal cual; lo que Odin agregue en el
futuro aparece sin actualizar este cliente. Hoy:

| Tool | Qué hace | Requiere |
|---|---|---|
| `whoami` | Alcance del token: scopes y apps que cubre | — |
| `sync_status` | Freshness del inventario (última sync por módulo) | `dashboard:read` |
| `search_ec2` | Busca instancias EC2 por nombre/IP/id | `ec2:read` |
| `checkpoint_search_users` | Usuarios VPN con grupos y destinos | `checkpoint:read` + app `checkpoint` |
| `checkpoint_group_report` | Destinos de un grupo VPN | `checkpoint:read` + app `checkpoint` |

Si tu token no cubre un scope/app, la tool responde con un mensaje de acceso
denegado (no filtra datos).

## Seguridad

Este cliente sigue el mismo modelo de mínimo privilegio que el MCP de Supabase:

- **Token de mínimo privilegio.** Crea el token con el preset *Solo lectura* y
  **solo** las apps que necesites. El token nunca puede más que tu usuario:
  sus permisos son un subconjunto de tu rol y de tus apps asignadas. El servidor
  re-valida en cada llamada (token no revocado/expirado, usuario activo).
- **Solo lectura.** Las tools no modifican nada en Odin ni en AWS/Checkpoint.
- **HTTPS obligatorio fuera de localhost.** El token viaja en el header
  `Authorization`; el cliente **rechaza** enviarlo por HTTP a un host remoto.
  Solo para labs internos puedes forzarlo con `ODIN_ALLOW_INSECURE=1` (bajo tu
  propio riesgo).
- **El token nunca se registra.** Los mensajes de error lo redactan.
- **Un token por persona/servicio.** No compartas tokens entre usuarios; así la
  trazabilidad (`last_used_at`) y la revocación son por token.
- **Caducidad.** Todos los tokens expiran. Rota por antigüedad; revoca los que
  no uses desde la UI de Odin.
- **Prompt injection.** Como con cualquier MCP, revisa lo que el agente hace con
  los datos. El servidor devuelve solo campos de inventario (nunca secretos,
  api keys ni hashes), pero el contenido es dato no confiable para el modelo.

## Cómo se mantiene actualizado

El servidor MCP es la fuente de verdad: cuando Odin se despliega con tools
nuevas, aparecen automáticamente aquí (este puente no las hardcodea). Solo
actualiza este paquete si cambia el protocolo de transporte.

## Licencia

MIT.
