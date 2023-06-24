import json
import time
import os
from Functions import MessageHandler, log_event, generate_blank_table
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from supabase_py import create_client, Client
from starlette.responses import Response
from starlette.types import Receive, Send, Scope

supabase_url = os.environ['SUPABASE_URL']
supabase_key = os.environ['SUPABASE_KEY']
supabase: Client = create_client(supabase_url, supabase_key)

class LoggingResponse(Response):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start_time = time.time()
        async def logging_send(message: dict) -> None:
            if message.get("type") == "http.response.body":
                body = message.get("body").decode()
                event = {
                    "Date": datetime.now().isoformat(),
                    "Method": scope["method"],
                    "Path": scope["path"],
                    "Status": self.status_code,
                    "Duration": time.time() - start_time,
                    "Event": body,
                    "Messages": message_handler.messages  # Add this line
                }
                log_event(supabase, event)
            await send(message)
        await super().__call__(scope, receive, logging_send)

app = FastAPI()

origins = ["https://chat.openai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/.well-known",
          StaticFiles(directory=".well-known"),
          name=".well-known")

class ProductData(BaseModel):
    user_input: Optional[str] = None

message_handler = MessageHandler()

@app.get("/")
def root():
    print_and_store("Root endpoint called")
    return LoggingResponse(content=json.dumps(
        {"message": "Welcome to ProductEngine"}),
        media_type="application/json")

@app.get("/get_status_messages")
async def get_status_messages():
    return LoggingResponse(content=json.dumps(
        {"messages": message_handler.messages[-15:]}),
        media_type="application/json")

@app.post("/generate_product_prototype")
async def generate_product_prototype(data: ProductData):
    print_and_store("generate_product_prototype endpoint called with user input: " + str(data.user_input))
    table = generate_blank_table()
    return LoggingResponse(content=json.dumps({"table": table, "message": "Fill in the rest, be clever, you're a marketing genuis."}), media_type="application/json")

@app.get("/ProductEngineLogo.png")
async def plugin_logo():
    print_and_store("logo.png endpoint called")
    return FileResponse("RecombLogo.png")

def print_and_store(message):
    message_handler.print_and_store(message, supabase)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
