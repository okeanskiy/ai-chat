from fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Create your FastMCP server with tools, resources, etc.
mcp = FastMCP("MyServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    print("[add] a: ", a, "b: ", b)
    return a + b

@mcp.resource("data://config")
def get_config() -> dict:
    """Get server configuration"""
    return {"version": "1.0", "environment": "production"}

# Create the ASGI app for the MCP server
mcp_app = mcp.http_app(path='/mcp')

# Create a FastAPI app and mount the MCP server
app = FastAPI(lifespan=mcp_app.lifespan)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello from FastAPI!</h1>
            <p>This is a test page.</p>
        </body>
    </html>
    """

app.mount("/mcp-server", mcp_app)