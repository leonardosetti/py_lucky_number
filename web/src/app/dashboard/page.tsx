"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { dashboard, getStoredToken, setAuthToken } from "@/services/api";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<{ total_usuarios: number; total_apostas: number; total_promessas: number } | null>(null);

  useEffect(() => {
    if (!getStoredToken()) {
      router.push("/login");
      return;
    }
    dashboard.summary().then(setData).catch(() => router.push("/login"));
  }, [router]);

  return (
    <main className="min-h-screen p-4" data-testid="dashboard-page">
      <h1 className="text-2xl font-bold mb-6" data-testid="dashboard-title">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white shadow rounded p-6" data-testid="dashboard-card-usuarios">
          <p className="text-gray-500 text-sm">Usuários</p>
          <p className="text-3xl font-bold" data-testid="dashboard-total-usuarios">{data?.total_usuarios ?? "—"}</p>
        </div>
        <div className="bg-white shadow rounded p-6" data-testid="dashboard-card-apostas">
          <p className="text-gray-500 text-sm">Apostas</p>
          <p className="text-3xl font-bold">{data?.total_apostas ?? "—"}</p>
        </div>
        <div className="bg-white shadow rounded p-6" data-testid="dashboard-card-promessas">
          <p className="text-gray-500 text-sm">Promessas</p>
          <p className="text-3xl font-bold">{data?.total_promessas ?? "—"}</p>
        </div>
      </div>

      <div className="flex gap-4 flex-wrap" data-testid="dashboard-actions">
        <a href="/generate" className="bg-green-600 text-white px-6 py-3 rounded hover:bg-green-700 min-h-[48px] flex items-center"
          data-testid="dashboard-btn-generate">Gerar Apostas</a>
        <a href="/history" className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 min-h-[48px] flex items-center"
          data-testid="dashboard-btn-history">Histórico</a>
        <a href="/promises" className="bg-purple-600 text-white px-6 py-3 rounded hover:bg-purple-700 min-h-[48px] flex items-center"
          data-testid="dashboard-btn-promises">Promessas</a>
        <button onClick={() => { setAuthToken(null); router.push("/login"); }}
          className="bg-gray-200 text-gray-700 px-6 py-3 rounded hover:bg-gray-300 min-h-[48px]"
          data-testid="dashboard-btn-logout">Sair</button>
      </div>
    </main>
  );
}
