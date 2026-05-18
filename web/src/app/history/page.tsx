"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { combinacoes, getStoredToken } from "@/services/api";

export default function HistoryPage() {
  const router = useRouter();
  const [items, setItems] = useState<Array<{ id: string; jogo: string; dezenas: number[]; favorita: boolean }>>([]);

  useEffect(() => {
    if (!getStoredToken()) { router.push("/login"); return; }
    combinacoes.list().then(setItems).catch(() => router.push("/login"));
  }, [router]);

  const toggleFav = async (id: string) => {
    await combinacoes.toggleFavorite(id);
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, favorita: !i.favorita } : i)));
  };

  const del = async (id: string) => {
    if (!confirm("Excluir combinação?")) return;
    await combinacoes.delete(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto" data-testid="history-page">
      <h1 className="text-2xl font-bold mb-6" data-testid="history-title">Histórico</h1>
      {items.length === 0 && (
        <div className="text-center py-12" data-testid="empty-state-history">
          <p className="text-gray-500 mb-4">Nenhuma combinação salva ainda.</p>
          <a href="/generate" className="bg-blue-600 text-white px-6 py-3 rounded inline-block" data-testid="empty-state-cta">Gerar Agora</a>
        </div>
      )}
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item.id} className="bg-white shadow rounded p-4 flex justify-between items-center" data-testid={`history-item-${item.id}`}>
            <div>
              <p className="font-bold">{item.jogo}</p>
              <p className="font-mono text-sm">{item.dezenas.map((n) => n.toString().padStart(2, "0")).join(" - ")}</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => toggleFav(item.id)} className={`text-2xl ${item.favorita ? "text-yellow-500" : "text-gray-300"}`}
                data-testid={`history-fav-${item.id}`}>★</button>
              <button onClick={() => del(item.id)} className="text-red-500 text-sm" data-testid={`history-del-${item.id}`}>Excluir</button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
