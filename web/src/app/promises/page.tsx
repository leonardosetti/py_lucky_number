"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { promessas, getStoredToken } from "@/services/api";

export default function PromisesPage() {
  const router = useRouter();
  const [items, setItems] = useState<Array<{ id: string; titulo: string; valor_total: number }>>([]);

  useEffect(() => {
    if (!getStoredToken()) { router.push("/login"); return; }
    promessas.list().then(setItems).catch(() => router.push("/login"));
  }, [router]);

  const handleDelete = async (id: string) => {
    if (!confirm("Excluir promessa?")) return;
    await promessas.delete(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const handleClone = async (id: string) => {
    const clone = await promessas.clone(id);
    setItems((prev) => [...prev, clone as { id: string; titulo: string; valor_total: number }]);
  };

  const handleShare = async (id: string) => {
    const res = await promessas.share(id);
    if (res?.link) {
      await navigator.clipboard.writeText(res.link);
      alert("Link copiado! Válido por 7 dias.");
    }
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto" data-testid="promises-page">
      <h1 className="text-2xl font-bold mb-6">Minhas Promessas</h1>
      {items.length === 0 && <div className="text-center py-12 text-gray-500" data-testid="empty-state-promises">Nenhuma promessa ainda.</div>}
      <ul className="space-y-2">
        {items.map((p) => (
          <li key={p.id} className="bg-white shadow rounded p-4 flex justify-between items-center" data-testid={`promise-${p.id}`}>
            <div>
              <p className="font-bold">{p.titulo || "Sem título"}</p>
              <p className="text-sm text-gray-600">R$ {p.valor_total.toFixed(2)}</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => handleShare(p.id)} className="text-green-600 text-sm px-2 py-1 border rounded"
                data-testid={`promise-share-${p.id}`}>Compartilhar</button>
              <button onClick={() => handleClone(p.id)} className="text-blue-600 text-sm px-2 py-1 border rounded"
                data-testid={`promise-clone-${p.id}`}>Clonar</button>
              <button onClick={() => handleDelete(p.id)} className="text-red-500 text-sm px-2 py-1 border rounded"
                data-testid={`promise-del-${p.id}`}>Excluir</button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
