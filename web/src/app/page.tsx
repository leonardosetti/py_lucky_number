import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 text-center" data-testid="landing-page">
      <h1 className="text-4xl font-bold mb-4" data-testid="landing-title">🍀 Lucky Number</h1>
      <p className="text-xl text-gray-600 mb-8 max-w-md">
        Gere combinações únicas para loterias da Caixa — números que nunca foram sorteados antes.
      </p>
      <div className="flex gap-4 flex-wrap justify-center" data-testid="landing-cta">
        <Link href="/register"
          className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-blue-700 min-h-[48px] flex items-center"
          data-testid="landing-btn-register">
          Criar Conta Gratuita
        </Link>
        <Link href="/login"
          className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg text-lg hover:bg-gray-300 min-h-[48px] flex items-center"
          data-testid="landing-btn-login">
          Já tenho conta
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-3xl">
        <div className="p-6 bg-white shadow rounded" data-testid="landing-feature-1">
          <h3 className="font-bold text-lg mb-2">🎲 Gerar</h3>
          <p className="text-gray-600">Combinações aleatórias validadas contra histórico real de sorteios.</p>
        </div>
        <div className="p-6 bg-white shadow rounded" data-testid="landing-feature-2">
          <h3 className="font-bold text-lg mb-2">💾 Salvar</h3>
          <p className="text-gray-600">Histórico FIFO com até 200 combinações e favoritos.</p>
        </div>
        <div className="p-6 bg-white shadow rounded" data-testid="landing-feature-3">
          <h3 className="font-bold text-lg mb-2">📤 Compartilhar</h3>
          <p className="text-gray-600">Exporte em CSV, JSON, PDF ou compartilhe via WhatsApp.</p>
        </div>
      </div>
    </main>
  );
}
