"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth, setAuthToken } from "@/services/api";

export default function RegisterPage() {
  const router = useRouter();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await auth.register(email, password, nome);
      setAuthToken(res.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao criar conta");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4" data-testid="register-page">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4" data-testid="register-form">
        <h1 className="text-2xl font-bold text-center">Criar Conta</h1>

        {error && <div className="bg-red-100 text-red-700 p-3 rounded" data-testid="error-register" role="alert">{error}</div>}

        <div>
          <label htmlFor="nome" className="block text-sm font-medium">Nome (opcional)</label>
          <input id="nome" type="text" value={nome} onChange={(e) => setNome(e.target.value)}
            className="w-full border rounded px-3 py-2 mt-1" data-testid="nome-input" />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium">Email</label>
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded px-3 py-2 mt-1" data-testid="email-input" required />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium">Senha</label>
          <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2 mt-1" data-testid="password-input" required minLength={6} />
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 min-h-[48px]"
          data-testid="register-submit-button">Criar Conta</button>
        <p className="text-center text-sm"><a href="/login" className="text-blue-600" data-testid="login-link">Já tenho conta</a></p>
      </form>
    </main>
  );
}
