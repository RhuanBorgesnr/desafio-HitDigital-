"""Configuração da aplicação, lida de variáveis de ambiente com defaults sãos.

Mantida simples de propósito (sem dependência extra): num desafio pequeno,
um objeto de settings legível vale mais que um framework de config.
"""
import os


class Settings:
    # URL base do provider externo. jsonplaceholder é público e serve bem:
    # ids 1..10 existem; 11+ retornam 404 -> demonstra `users` e `failed`.
    provider_base_url: str = os.getenv(
        "PROVIDER_BASE_URL", "https://jsonplaceholder.typicode.com"
    )
    # Timeout por requisição ao provider (segundos).
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
    # Teto de requisições simultâneas ao provider (controle de concorrência).
    max_concurrency: int = int(os.getenv("MAX_CONCURRENCY", "10"))


settings = Settings()
