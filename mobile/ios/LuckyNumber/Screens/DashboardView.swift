import SwiftUI

struct DashboardView: View {
    @State private var usuarios = 0
    @State private var apostas = 0
    @State private var promessas = 0

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    CardView(title: "Usuários", value: "\(usuarios)", color: .blue)
                    CardView(title: "Apostas", value: "\(apostas)", color: .green)
                    CardView(title: "Promessas", value: "\(promessas)", color: .purple)
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .refreshable { await loadData() }
            .task { await loadData() }
        }
    }

    func loadData() async {
        guard let res = try? await APIClient.shared.getDashboard() else { return }
        await MainActor.run {
            usuarios = res.total_usuarios
            apostas = res.total_apostas
            promessas = res.total_promessas
        }
    }
}

struct CardView: View {
    let title: String; let value: String; let color: Color
    var body: some View {
        VStack(alignment: .leading) {
            Text(title).font(.subheadline).foregroundColor(.gray)
            Text(value).font(.largeTitle).bold()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}
