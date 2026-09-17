"""Contratos de entrada e saída da API (validação + forma da resposta).

Com Pydantic, a validação do requisito 1 sai "de graça": entrada inválida
vira 422 automaticamente, sem código manual.
"""
from pydantic import BaseModel, Field, field_validator


class FetchRequest(BaseModel):
    # 1..100 ids: lista vazia -> 422; acima de 100 evita abuso trivial.
    user_ids: list[int] = Field(..., min_length=1, max_length=100)

    @field_validator("user_ids")
    @classmethod
    def positive_and_unique(cls, ids: list[int]) -> list[int]:
        if any(i <= 0 for i in ids):
            raise ValueError("user_ids devem ser inteiros positivos")
        # Remove duplicados preservando a ordem (não consulta o mesmo id 2x).
        return list(dict.fromkeys(ids))


class User(BaseModel):
    id: int
    name: str


class FetchResponse(BaseModel):
    users: list[User]
    failed: list[int]
