import SwiftUI

struct LoginView: View {
    @EnvironmentObject var auth: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var showBiometric = false

    var body: some View {
        VStack(spacing: 20) {
            Text("🍀 Lucky Number").font(.largeTitle).bold()
            Text("Faça login para continuar").foregroundColor(.gray)

            TextField("Email", text: $email)
                .textFieldStyle(.roundedBorder).keyboardType(.emailAddress)
                .accessibility(label: Text("Email"))
            SecureField("Senha", text: $password)
                .textFieldStyle(.roundedBorder)
                .accessibility(label: Text("Senha"))

            Button("Entrar") { auth.login(email: email, password: password) }
                .buttonStyle(.borderedProminent).frame(maxWidth: .infinity).frame(height: 48)

            if BiometricHelper.shared.isAvailable() {
                Button("Usar Biometria") { showBiometric = true }
                    .buttonStyle(.bordered)
            }
        }
        .padding()
        .onAppear {
            if auth.canUseBiometric() { showBiometric = true }
        }
        .sheet(isPresented: $showBiometric) {
            BiometricAuthView { auth.loginWithBiometric() }
        }
    }
}
