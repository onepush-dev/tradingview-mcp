# tradingview-mcp on Railway: the official upstream image (atilaahmettaner/tradingview-mcp 0.8.0, MIT), app unmodified.
# This layer adds railway/serve.py: the same FastMCP server over streamable HTTP on port 8080 with a bearer-token
# gate (MCP_AUTH_TOKEN), because the upstream HTTP transport has no authentication.
FROM ghcr.io/atilaahmettaner/tradingview-mcp:0.8.0
LABEL org.opencontainers.image.source="https://github.com/onepush-dev/tradingview-mcp"
COPY railway/serve.py /app/railway_serve.py
ENV HOST=0.0.0.0 MCP_PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080
ENTRYPOINT ["python", "/app/railway_serve.py"]
CMD []
