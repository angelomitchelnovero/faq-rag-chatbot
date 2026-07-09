"""
FastAPI entrypoint for the FAQ RAG Chatbot backend.

This is a placeholder for Step 1 (scaffolding).
Full app setup (config, routers, CORS, startup events) is built in Step 2.
"""
from fastapi import FastAPI

app = FastAPI(title="FAQ RAG Chatbot API")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "FAQ RAG Chatbot API is running"}
