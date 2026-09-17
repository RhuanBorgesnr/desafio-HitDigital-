"""Interface do provider de usuários.

O service depende DESTA abstração, não de uma implementação concreta. Trocar
jsonplaceholder por outra API (ou por um mock) é só passar outro objeto que
satisfaça este Protocol — a regra de negócio não muda uma linha.
"""
from typing import Protocol

from app.schemas import User


class UserProvider(Protocol):
    async def get_user(self, user_id: int) -> User:
        """Retorna um usuário ou levanta uma exceção de `app.errors`
        (UserNotFound, ProviderTimeout, ProviderUnavailable)."""
        ...
