"""Railway launcher for tradingview-mcp (upstream app unmodified).

Serves the upstream FastMCP server over streamable HTTP on 0.0.0.0:8080 and puts a bearer-token gate in
front of it, because the upstream HTTP transport has no authentication of its own. /health stays open for
Railway's healthcheck. Clients send `Authorization: Bearer <MCP_AUTH_TOKEN>` (or `?token=<MCP_AUTH_TOKEN>`
for clients that cannot set headers). Leave MCP_AUTH_TOKEN empty to run a public read-only endpoint.
"""
import hmac
import os
from urllib.parse import parse_qs

import uvicorn
from tradingview_mcp.server import mcp

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("MCP_PORT", "8080"))
TOKEN = os.environ.get("MCP_AUTH_TOKEN", "").strip()
OPEN_PATHS = {"/health"}

mcp.settings.host = HOST
mcp.settings.port = PORT
# Railway's edge forwards the public hostname; the upstream DNS-rebinding guard only allows localhost
# when host is 127.0.0.1, so it is disabled here (the bearer token is the protection instead).
try:
    mcp.settings.transport_security.enable_dns_rebinding_protection = False
except Exception:
    pass

inner = mcp.streamable_http_app()


def _authorized(scope) -> bool:
    if not TOKEN or scope.get("path") in OPEN_PATHS:
        return True
    headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
    auth = headers.get("authorization", "")
    if auth.lower().startswith("bearer ") and hmac.compare_digest(auth[7:].strip(), TOKEN):
        return True
    q = parse_qs(scope.get("query_string", b"").decode())
    return bool(q.get("token")) and hmac.compare_digest(q["token"][0], TOKEN)


async def app(scope, receive, send):
    if scope["type"] == "http" and scope.get("path") == "/health":
        await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": b'{"status":"ok"}'})
        return
    if scope["type"] == "http" and not _authorized(scope):
        body = b'{"error":"unauthorized","hint":"send Authorization: Bearer <MCP_AUTH_TOKEN>"}'
        await send({"type": "http.response.start", "status": 401,
                    "headers": [(b"content-type", b"application/json"), (b"www-authenticate", b"Bearer")]})
        await send({"type": "http.response.body", "body": body})
        return
    await inner(scope, receive, send)


if __name__ == "__main__":
    print(f"railway: tradingview-mcp streamable HTTP on {HOST}:{PORT} (MCP endpoint /mcp, auth "
          f"{'bearer token required' if TOKEN else 'OFF: public endpoint'})", flush=True)
    uvicorn.run(app, host=HOST, port=PORT, proxy_headers=True, forwarded_allow_ips="*")
