# Consulta de usuários

Aplicação Full Stack que recebe uma lista de IDs, consulta cada usuário em uma
API HTTP externa **de forma assíncrona** e devolve, separadamente, os usuários
obtidos e os IDs que falharam. A falha de um usuário **não** interrompe os demais.

- **Backend:** Python + FastAPI (async, `httpx`, validação com Pydantic).
- **Frontend:** React + TypeScript (Vite).
- **Provider externo:** [jsonplaceholder](https://jsonplaceholder.typicode.com)
  (IDs 1–10 existem; 11+ retornam 404 — ótimo para ver `users` e `failed`).

```
POST /api/users/fetch
{ "user_ids": [1, 2, 3, 11] }
->
{ "users": [{ "id": 1, "name": "Leanne Graham" }, ...], "failed": [11] }
```

## Como executar

### Backend (porta 8000)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs interativas em `http://localhost:8000/docs`.

### Frontend (porta 5173)

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Se o backend não estiver em `localhost:8000`,
defina `VITE_API_URL`.

### Testes

```bash
cd backend
pytest
```