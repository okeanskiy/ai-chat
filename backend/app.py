from fastapi import FastAPI
import uvicorn
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from openai.types.responses import ResponseTextDeltaEvent

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

lorem_ipsum = "Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of \"de Finibus Bonorum et Malorum\" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, \"Lorem ipsum dolor sit amet..\", comes from a line in section 1.10.32."

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/backend_status")
def backend_status():
    return HTMLResponse(content="<h1>Backend is running</h1>")

async def stream_lorem_ipsum():
    words = lorem_ipsum.split()
    for i in range(0, len(words), 4):
        chunk = " ".join(words[i:i+4])
        if i < len(words) - 4:
            chunk += " "
        yield chunk
        await asyncio.sleep(0.2)

async def stream_openai_response(query: str):
    print("[stream_openai_response] query: ", query)

    async with MCPServerStreamableHttp(
        name="mcp_test_server",
        params={"url": "http://127.0.0.1:8002/mcp-server/mcp/"}
    ) as mcp_server:
        agent = Agent(
            name="C# coding assistant",
            instructions="You are a helpful C# coding assistant.",
            model="gpt-4.1",
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(tool_choice="auto"),
        )

        result = Runner.run_streamed(agent, input=query)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield event.data.delta

@app.get("/stream")
async def stream():
    return StreamingResponse(stream_lorem_ipsum(), media_type="text/plain")

@app.get("/stream_llm")
async def stream_llm(query: str):
    return StreamingResponse(stream_openai_response(query), media_type="text/plain")
