"""Implementação real do provider, sobre uma API HTTP externa (httpx, async).

Único lugar do código que sabe que existe httpx e um endpoint remoto. Traduz
toda falha de transporte/HTTP para as exceções de domínio de `app.errors`.
"""
import httpx

from app.errors import ProviderTimeout, ProviderUnavailable, UserNotFound
from app.schemas import User


class HttpUserProvider:
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        # Cliente injetado (criado uma vez no ciclo de vida da app) para
        # reaproveitar conexões — importante ao consultar muitos ids.
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def get_user(self, user_id: int) -> User:
        url = f"{self._base_url}/users/{user_id}"
        try:
            response = await self._client.get(url)
        except httpx.TimeoutException as exc:
            raise ProviderTimeout(user_id) from exc
        except httpx.HTTPError as exc:  # erros de rede/transporte
            raise ProviderUnavailable(user_id) from exc

        if response.status_code == 404:
            raise UserNotFound(user_id)
        if response.status_code >= 400:
            raise ProviderUnavailable(user_id)

        data = response.json()
        # Normaliza: o front recebe só o que precisa, não o JSON cru do provider.
        return User(id=data["id"], name=data["name"])
