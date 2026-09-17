"""Provider em memória, usado nos testes (e útil para rodar sem internet).

Prova, na prática, que a regra de negócio não depende de HTTP: os testes
exercitam o `fetch_users` real trocando apenas o provider.
"""
import asyncio

from app.errors import ProviderTimeout, UserNotFound
from app.schemas import User


class FakeUserProvider:
    def __init__(
        self,
        users: dict[int, str],
        not_found: set[int] | None = None,
        timeout: set[int] | None = None,
    ) -> None:
        self._users = users
        self._not_found = not_found or set()
        self._timeout = timeout or set()

    async def get_user(self, user_id: int) -> User:
        await asyncio.sleep(0)  # cede o loop, simulando I/O assíncrono
        if user_id in self._timeout:
            raise ProviderTimeout(user_id)
        if user_id in self._not_found or user_id not in self._users:
            raise UserNotFound(user_id)
        return User(id=user_id, name=self._users[user_id])
