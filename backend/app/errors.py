"""Exceções de domínio da integração externa.

A regra de negócio (service) e as rotas conhecem SÓ estas exceções, nunca
detalhes de httpx. Isso é o que permite trocar o provider sem reescrever a
regra: cada provider traduz suas falhas para este vocabulário.
"""


class ProviderError(Exception):
    """Base de qualquer falha ao consultar o provider externo."""

    def __init__(self, user_id: int, message: str) -> None:
        self.user_id = user_id
        super().__init__(message)


class UserNotFound(ProviderError):
    def __init__(self, user_id: int) -> None:
        super().__init__(user_id, f"usuário {user_id} não encontrado")


class ProviderTimeout(ProviderError):
    def __init__(self, user_id: int) -> None:
        super().__init__(user_id, f"timeout ao consultar usuário {user_id}")


class ProviderUnavailable(ProviderError):
    """Erro HTTP inesperado (5xx, 4xx que não seja 404) ou falha de rede."""

    def __init__(self, user_id: int) -> None:
        super().__init__(user_id, f"provider indisponível ao consultar usuário {user_id}")
