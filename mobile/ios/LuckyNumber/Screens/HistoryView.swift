import SwiftUI

struct HistoryView: View {
    @State private var items: [CombinacaoResponse] = []

    var body: some View {
        NavigationView {
            List {
                if items.isEmpty {
                    VStack(spacing: 12) {
                        Text("📭").font(.system(size: 48))
                        Text("Nenhuma combinação ainda").foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity).padding(.vertical, 60)
                }
                ForEach(items, id: \.id) { item in
                    HStack {
                        VStack(alignment: .leading) {
                            Text(item.jogo).font(.headline)
                            Text(item.dezenas.map { String(format: "%02d", $0) }.joined(separator: " - "))
                                .font(.caption).foregroundColor(.gray)
                        }
                        Spacer()
                        Image(systemName: item.favorita ? "star.fill" : "star")
                            .foregroundColor(item.favorita ? .yellow : .gray)
                            .onTapGesture { /* toggle favorite */ }
                    }
                    .swipeActions(edge: .trailing) {
                        Button("Excluir", role: .destructive) { delete(item.id) }
                    }
                }
            }
            .navigationTitle("Histórico")
            .refreshable { await load() }
            .task { await load() }
        }
    }

    func load() async {
        guard let res = try? await APIClient.shared.getCombinacoes() else { return }
        await MainActor.run { items = res }
    }

    func delete(_ id: String) {
        items.removeAll { $0.id == id }
    }
}

extension APIClient {
    func getCombinacoes() async throws -> [CombinacaoResponse] {
        try await request("/combinacoes")
    }
}
