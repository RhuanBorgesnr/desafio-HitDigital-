import { useState } from "react";
import { fetchUsers, type FetchResult } from "./api";

function parseIds(text: string): number[] {
  return text
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0)
    .map(Number)
    .filter((n) => Number.isInteger(n) && n > 0);
}

export function App() {
  const [raw, setRaw] = useState("1, 2, 3, 11");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FetchResult | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const ids = parseIds(raw);
    if (ids.length === 0) {
      setError("Informe ao menos um ID válido (inteiro positivo).");
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await fetchUsers(ids));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>Consulta de usuários</h1>

      <form onSubmit={onSubmit} className="form">
        <label htmlFor="ids">IDs separados por vírgula</label>
        <input
          id="ids"
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder="ex.: 1, 2, 3, 11"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Consultando…" : "Consultar"}
        </button>
      </form>


      {loading && <p className="muted">Consultando usuários…</p>}

      {error && <p className="error" role="alert">{error}</p>}


      {result && (
        <div className="results">
          <section>
            <h2>Encontrados ({result.users.length})</h2>
            {result.users.length === 0 ? (
              <p className="muted">Nenhum usuário encontrado.</p>
            ) : (
              <ul>
                {result.users.map((u) => (
                  <li key={u.id}>
                    <strong>#{u.id}</strong> — {u.name}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h2>Falharam ({result.failed.length})</h2>
            {result.failed.length === 0 ? (
              <p className="muted">Nenhuma falha.</p>
            ) : (
              <ul className="failed">
                {result.failed.map((id) => (
                  <li key={id}>#{id}</li>
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </main>
  );
}
