"""Camada HTTP: cria o app, injeta o provider e expõe o endpoint.

Fino de propósito — toda a lógica vive em `services` e `providers`.
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.providers.http_provider import HttpUserProvider
from app.schemas import FetchRequest, FetchResponse
from app.services import fetch_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Um único AsyncClient para toda a app -> reuso de conexões (pool).
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        app.state.provider = HttpUserProvider(settings.provider_base_url, client)
        yield


app = FastAPI(title="Consulta de usuários", lifespan=lifespan)

# CORS liberado para o front local (Vite). Em produção seria uma allowlist.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/users/fetch", response_model=FetchResponse)
async def fetch(request_body: FetchRequest, request: Request) -> FetchResponse:
    # FastAPI já validou o corpo (requisito 1). Delegamos à regra de negócio.
    provider = request.app.state.provider
    return await fetch_users(provider, request_body.user_ids, settings.max_concurrency)
