import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var auth: AuthViewModel

    var body: some View {
        NavigationView {
            Form {
                Section("Conta") {
                    Text("admin@luckynumber.app")
                    Button("Alterar Senha") { /* T157 — requires new API */ }
                        .disabled(true).foregroundColor(.gray)
                }
                Section("Aparência") {
                    Toggle("Modo Escuro", isOn: .constant(false))
                }
                Section {
                    Button("Sair", role: .destructive) { auth.logout() }
                }
            }
            .navigationTitle("Perfil")
        }
    }
}
