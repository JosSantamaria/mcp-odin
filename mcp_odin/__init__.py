"""mcp-odin — cliente puente para el MCP de Odin.

Conecta clientes MCP locales (Claude Desktop, Cursor, Kiro, etc.) que hablan por
stdio con el servidor MCP de Odin, que es remoto y habla streamable-http con
autenticación por API token.

No contiene ningún secreto: el token y la URL se leen del entorno del usuario.
"""

__version__ = "0.1.0"
