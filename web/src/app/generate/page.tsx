"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { bets, combinacoes, getStoredToken } from "@/services/api";

const GAMES = ["megasena", "lotofacil", "quina", "duplasena", "federal", "diadesorte"];

export default function GeneratePage() {
  const router = useRouter();
  const [jogo, setJogo] = useState("megasena");
  const [quantidade, setQuantidade] = useState(1);
  const [dezenas, setDezenas] = useState(6);
  const [result, setResult] = useState<number[][] | null>(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");

  if (typeof window !== "undefined" && !getStoredToken()) router.push("/login");

  const handleGenerate = async () => {
    setError(""); setResult(null);
    try {
      const res = await bets.generate(jogo, quantidade, dezenas);
      setResult(res.apostas);
      setTotal(res.valor_total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao gerar");
    }
  };

  const handleSave = async () => {
    if (!result) return;
    for (const nums of result) {
      try { await combinacoes.save(jogo, nums, dezenas); } catch { /* ignore duplicates */ }
    }
    alert("Combinações salvas no histórico!");
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto" data-testid="generate-page">
      <h1 className="text-2xl font-bold mb-6" data-testid="generate-title">Gerar Apostas</h1>

      <div className="space-y-4 bg-white shadow rounded p-6">
        <div>
          <label className="block text-sm font-medium mb-1">Jogo</label>
          <select value={jogo} onChange={(e) => setJogo(e.target.value)}
            className="w-full border rounded px-3 py-2" data-testid="generate-game-select">
            {GAMES.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Quantidade (1–10)</label>
          <input type="number" min={1} max={10} value={quantidade}
            onChange={(e) => setQuantidade(Number(e.target.value))}
            className="w-full border rounded px-3 py-2" data-testid="generate-quantity" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Dezenas por aposta</label>
          <input type="number" min={6} max={20} value={dezenas}
            onChange={(e) => setDezenas(Number(e.target.value))}
            className="w-full border rounded px-3 py-2" data-testid="generate-numbers" />
        </div>

        <button onClick={handleGenerate}
          className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 min-h-[48px] font-bold"
          data-testid="generate-submit-button">Gerar</button>

        {error && <div className="bg-red-100 text-red-700 p-3 rounded" data-testid="error-generate">{error}</div>}

        {result && (
          <div data-testid="generate-result">
            <h2 className="font-bold mb-2">Resultado</h2>
            <p className="text-sm text-gray-600 mb-2">Valor total: R$ {total.toFixed(2)}</p>
            <ul className="space-y-1">
              {result.map((nums, i) => (
                <li key={i} className="font-mono bg-gray-50 p-2 rounded" data-testid={`generate-result-${i}`}>
                  {nums.map((n) => n.toString().padStart(2, "0")).join(" - ")}
                </li>
              ))}
            </ul>
            <button onClick={handleSave}
              className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 min-h-[48px]"
              data-testid="generate-save-button">Salvar no Histórico</button>
          </div>
        )}
      </div>
    </main>
  );
}
