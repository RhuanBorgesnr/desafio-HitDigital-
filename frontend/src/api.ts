// Camada de acesso ao backend: tipos + a chamada HTTP num só lugar.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface User {
  id: number;
  name: string;
}

export interface FetchResult {
  users: User[];
  failed: number[];
}

export async function fetchUsers(userIds: number[]): Promise<FetchResult> {
  const response = await fetch(`${API_URL}/api/users/fetch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_ids: userIds }),
  });

  if (!response.ok) {
    // Traduz o erro do backend numa mensagem legível para a UI.
    let detail = `Erro ${response.status} do servidor`;
    try {
      const body = await response.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      // resposta sem corpo JSON — mantém a mensagem padrão
    }
    throw new Error(detail);
  }

  return response.json();
}
