"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth, setAuthToken } from "@/services/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await auth.login(email, password);
      setAuthToken(res.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao fazer login");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4" data-testid="login-page">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4" data-testid="login-form">
        <h1 className="text-2xl font-bold text-center">Lucky Number</h1>
        <p className="text-center text-gray-600">Faça login para continuar</p>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded" data-testid="error-login" role="alert">
            {error}
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium">Email</label>
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded px-3 py-2 mt-1" data-testid="email-input" required />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium">Senha</label>
          <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2 mt-1" data-testid="password-input" required />
        </div>

        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 min-h-[48px]"
          data-testid="login-submit-button">
          Entrar
        </button>

        <p className="text-center text-sm">
          <a href="/register" className="text-blue-600" data-testid="register-link">Criar conta</a>
        </p>
      </form>
    </main>
  );
}
