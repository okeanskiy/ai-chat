from fastapi import FastAPI
import uvicorn
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

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

@app.get("/stream")
async def stream():
    return StreamingResponse(stream_lorem_ipsum(), media_type="text/plain")
