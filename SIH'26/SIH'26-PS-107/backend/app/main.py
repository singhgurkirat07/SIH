# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import conversation, explorer, lab_discovery

app = FastAPI(
    title="BIS Assist API",
    description="Backend services for Indian Standards and BIS Services Assistant.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversation.router)
app.include_router(explorer.router)
app.include_router(lab_discovery.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
