from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.booth import router as booth_router
from src.api.candidate import router as candidate_router
from src.api.manifesto import router as manifesto_router


app = FastAPI(
    title="CivikSutra API",
    description="Election process education APIs.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5000",
        "https://civiksutra-2604261729.web.app",
        "https://civiksutra-2604261729.firebaseapp.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(booth_router)
app.include_router(candidate_router)
app.include_router(manifesto_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
