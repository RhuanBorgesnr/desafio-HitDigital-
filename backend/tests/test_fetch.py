import pytest

from app.providers.fake_provider import FakeUserProvider
from app.services import fetch_users


@pytest.mark.asyncio
async def test_consulta_com_sucesso():
    provider = FakeUserProvider({1: "Alice", 2: "Bob"})

    result = await fetch_users(provider, [1, 2], max_concurrency=5)

    assert [u.id for u in result.users] == [1, 2]
    assert [u.name for u in result.users] == ["Alice", "Bob"]
    assert result.failed == []


@pytest.mark.asyncio
async def test_falha_de_um_nao_interrompe_os_demais():
    # id 2 não existe e id 4 dá timeout; 1 e 3 devem vir normalmente.
    provider = FakeUserProvider(
        {1: "Alice", 3: "Carol", 4: "Dan"},
        not_found={2},
        timeout={4},
    )

    result = await fetch_users(provider, [1, 2, 3, 4], max_concurrency=5)

    assert {u.id for u in result.users} == {1, 3}
    assert result.failed == [2, 4]
