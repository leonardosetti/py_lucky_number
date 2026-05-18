"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { notifications, getStoredToken } from "@/services/api";

export default function NotificationsPage() {
  const router = useRouter();
  const [items, setItems] = useState<Array<{ id: string; lida: boolean; created_at: string }>>([]);

  useEffect(() => {
    if (!getStoredToken()) { router.push("/login"); return; }
    notifications.list().then(setItems).catch(() => router.push("/login"));
  }, [router]);

  const markRead = async (id: string) => {
    await notifications.markRead(id);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, lida: true } : n)));
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto" data-testid="notifications-page">
      <h1 className="text-2xl font-bold mb-6" data-testid="notifications-title">Notificações</h1>
      {items.length === 0 && (
        <div className="text-center py-12 text-gray-500" data-testid="empty-state-notifications">
          Nenhuma notificação.
        </div>
      )}
      <ul className="space-y-2">
        {items.map((n) => (
          <li key={n.id}
            className={`bg-white shadow rounded p-4 flex justify-between items-center ${n.lida ? "opacity-60" : ""}`}
            data-testid={`notification-${n.id}`}>
            <div>
              <p className={n.lida ? "" : "font-bold"}>{n.id.slice(0, 8)}...</p>
              <p className="text-xs text-gray-400">{n.created_at}</p>
            </div>
            {!n.lida && (
              <button onClick={() => markRead(n.id)}
                className="text-blue-600 text-sm px-3 py-1 border rounded" data-testid={`notification-read-${n.id}`}>
                Marcar como lida
              </button>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
