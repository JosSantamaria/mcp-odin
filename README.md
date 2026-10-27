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
export ODIN_MCP_URL="https://odin.macropay.mx/mcp/"   # o el de QA
export ODIN_API_TOKEN="odin_xxxxxxxx..."              # tu token personal
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
        "ODIN_MCP_URL": "https://odin.macropay.mx/mcp/",
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

## Cómo se mantiene actualizado

El servidor MCP es la fuente de verdad: cuando Odin se despliega con tools
nuevas, aparecen automáticamente aquí (este puente no las hardcodea). Solo
actualiza este paquete si cambia el protocolo de transporte.

## Licencia

MIT.
