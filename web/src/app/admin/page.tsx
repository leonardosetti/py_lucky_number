"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { notifications, features as featuresApi, getStoredToken } from "@/services/api";

export default function AdminPage() {
  const router = useRouter();
  const [feats, setFeats] = useState<Array<{ slug: string; nome: string; ativa: boolean }>>([]);

  useEffect(() => {
    if (!getStoredToken()) { router.push("/login"); return; }
    featuresApi.list().then(setFeats).catch(() => {});
  }, [router]);

  const toggle = async (slug: string) => {
    await featuresApi.toggle(slug);
    setFeats((prev) => prev.map((f) => (f.slug === slug ? { ...f, ativa: !f.ativa } : f)));
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto" data-testid="admin-page">
      <h1 className="text-2xl font-bold mb-6" data-testid="admin-title">Administração</h1>

      <section className="bg-white shadow rounded p-6 mb-6" data-testid="admin-features">
        <h2 className="font-bold text-lg mb-4">Features</h2>
        {feats.map((f) => (
          <div key={f.slug} className="flex justify-between items-center py-2 border-b" data-testid={`feature-${f.slug}`}>
            <div>
              <p className="font-medium">{f.nome}</p>
              <p className="text-sm text-gray-500">{f.slug}</p>
            </div>
            <button onClick={() => toggle(f.slug)}
              className={`px-4 py-2 rounded text-white min-h-[44px] ${f.ativa ? "bg-green-600" : "bg-gray-400"}`}
              data-testid={`feature-toggle-${f.slug}`}>{f.ativa ? "Ativa" : "Inativa"}</button>
          </div>
        ))}
      </section>
    </main>
  );
}
