import Foundation
import LocalAuthentication

// Prevents CWE-522: tokens in Keychain via KeychainHelper
class AuthViewModel: ObservableObject {
    @Published var isLoggedIn = false
    @Published var token: String? = nil
    private let keychain = KeychainHelper()
    private let api = APIClient.shared

    init() {
        if let stored = try? keychain.get("jwt") {
            token = stored
            isLoggedIn = true
        }
    }

    func login(email: String, password: String) {
        Task {
            do {
                let res = try await api.login(email: email, password: password)
                await MainActor.run {
                    token = res.access_token
                    try? keychain.save(res.access_token, key: "jwt")
                    isLoggedIn = true
                }
            } catch {
                await MainActor.run { /* show error */ }
            }
        }
    }

    func loginWithBiometric() {
        // Biometric already authenticated — use stored token
        if let stored = try? keychain.get("jwt") {
            token = stored
            isLoggedIn = true
        }
    }

    func canUseBiometric() -> Bool {
        return BiometricHelper.shared.isAvailable()
    }

    func logout() {
        keychain.delete("jwt")
        token = nil
        isLoggedIn = false
    }
}

// Prevents CWE-287: biometric authentication with LAContext
struct BiometricHelper {
    static let shared = BiometricHelper()

    func isAvailable() -> Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    func authenticate(reason: String = "Acessar Lucky Number") async throws -> Bool {
        let context = LAContext()
        return try await context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason)
    }
}

struct BiometricAuthView: View {
    let onSuccess: () -> Void
    var body: some View {
        VStack { Text("Autentique-se para continuar"); ProgressView() }
            .onAppear {
                Task {
                    if (try? await BiometricHelper.shared.authenticate()) != nil {
                        onSuccess()
                    }
                }
            }
    }
}
