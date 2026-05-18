import SwiftUI

// Main tab view — Bottom Tab Navigation (Constitution VII)
struct ContentView: View {
    @EnvironmentObject var auth: AuthViewModel
    @State private var selectedTab = 0

    var body: some View {
        if auth.isLoggedIn {
            TabView(selection: $selectedTab) {
                DashboardView()
                    .tabItem { Label("Início", systemImage: "house") }
                    .tag(0)

                GenerateView()
                    .tabItem { Label("Gerar", systemImage: "dice") }
                    .tag(1)

                HistoryView()
                    .tabItem { Label("Histórico", systemImage: "clock") }
                    .tag(2)

                ProfileView()
                    .tabItem { Label("Perfil", systemImage: "person") }
                    .tag(3)
            }
        } else {
            LoginView()
        }
    }
}
