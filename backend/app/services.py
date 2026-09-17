"""Regra de negócio: consulta N usuários em paralelo, isolando falhas.

Esta função é o coração do desafio e não conhece HTTP: recebe qualquer objeto
que satisfaça `UserProvider`. Requisitos atendidos aqui:
  (3) consultas assíncronas;
  (4) a falha de um id não interrompe os demais;
  (6) retorno separando obtidos e falhados.
"""
import asyncio
import logging

from app.providers.base import UserProvider
from app.schemas import FetchResponse, User

logger = logging.getLogger("users.fetch")


async def fetch_users(
    provider: UserProvider,
    user_ids: list[int],
    max_concurrency: int,
) -> FetchResponse:
    # Semáforo = controle explícito de concorrência: dispara tudo "ao mesmo
    # tempo", mas no máximo `max_concurrency` chamadas ativas no provider.
    semaphore = asyncio.Semaphore(max_concurrency)

    async def fetch_one(user_id: int) -> User:
        async with semaphore:
            return await provider.get_user(user_id)

    # return_exceptions=True: uma exceção vira um item do resultado em vez de
    # abortar o gather. É isso que garante o requisito (4).
    results = await asyncio.gather(
        *(fetch_one(uid) for uid in user_ids),
        return_exceptions=True,
    )

    users: list[User] = []
    failed: list[int] = []
    for user_id, result in zip(user_ids, results):
        if isinstance(result, User):
            users.append(result)
        else:
            failed.append(user_id)
            logger.warning(
                "falha ao consultar usuário %s: %s",
                user_id,
                type(result).__name__,
            )

    return FetchResponse(users=users, failed=failed)
