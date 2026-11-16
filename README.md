# TradingView MCP Server on Railway

[tradingview-mcp](https://github.com/atilaahmettaner/tradingview-mcp) (MIT) — an MCP server with 37 market-data tools (crypto, stock and futures screeners, technical analysis, Bollinger/candle scans, backtesting, sentiment) for Claude, Cursor and other MCP clients. Deploy it as a private remote MCP endpoint on Railway with one click.

> Independent open-source project, not affiliated with or endorsed by TradingView Inc. "TradingView" is a trademark of its owner. This template is not affiliated with the upstream author either.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/79Oqng)

## What this template runs

- **tradingview-mcp**: `ghcr.io/onepush-dev/tradingview-mcp:0.8.0`, the official `ghcr.io/atilaahmettaner/tradingview-mcp:0.8.0` image (app unmodified) plus `railway/serve.py`, which serves the same server over streamable HTTP on port 8080 behind a bearer-token check. Public HTTPS domain, healthcheck `/health`, no volume (stateless).

## Variables

| Variable | Value | Notes |
|---|---|---|
| `MCP_AUTH_TOKEN` | generated secret | Clients must send `Authorization: Bearer <token>`. Empty = public endpoint. |

Baked into the image: `HOST=0.0.0.0`, `MCP_PORT=8080`.

## Connect a client

MCP endpoint: `https://<your-domain>/mcp`, header `Authorization: Bearer <MCP_AUTH_TOKEN>` (copy it from the service's Variables tab). Example for clients that read `mcpServers` JSON:

```json
{
  "mcpServers": {
    "tradingview": {
      "type": "http",
      "url": "https://<your-domain>/mcp",
      "headers": { "Authorization": "Bearer <MCP_AUTH_TOKEN>" }
    }
  }
}
```

Clients that cannot set headers can use `https://<your-domain>/mcp?token=<MCP_AUTH_TOKEN>`.

## Notes

- Optional: `MARKETAUX_API_TOKEN` enables the news tools; `PROXY_*` variables route requests through a Webshare proxy if the data source rate-limits Railway's IP.
- Market data is for research only, not financial advice.
