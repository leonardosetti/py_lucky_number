import Foundation

// Lucky Number API Client — Swift
// Prevents CWE-918 (SSRF): fixed base URL
// Prevents CWE-522: Keychain storage

class APIClient {
    static let shared = APIClient()
    private let baseURL = "http://localhost:8000/api/v1"
    private let session: URLSession
    private let keychain = KeychainHelper()

    init() {
        // Prevents CWE-295: certificate pinning
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }

    private func request<T: Decodable>(_ path: String, method: String = "GET", body: Data? = nil) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = try? keychain.get("jwt") {
            req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let body = body { req.httpBody = body }

        let (data, response) = try await session.data(for: req)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        return try JSONDecoder().decode(T.self, from: data)
    }

    // MARK: - Auth
    func login(email: String, password: String) async throws -> TokenResponse {
        let body = ["email": email, "password": password]
        let data = try JSONSerialization.data(withJSONObject: body)
        return try await request("/auth/login", method: "POST", body: data)
    }

    func register(email: String, password: String, nome: String) async throws -> TokenResponse {
        let body = ["email": email, "password": password, "nome": nome]
        let data = try JSONSerialization.data(withJSONObject: body)
        return try await request("/auth/register", method: "POST", body: data)
    }

    // MARK: - Features
    func getFeatures() async throws -> [FeatureResponse] {
        try await request("/admin/features")
    }

    // MARK: - Bets
    func gerarApostas(jogo: String, quantidade: Int, dezenas: Int) async throws -> BetResponse {
        let body: [String: Any] = ["jogo": jogo, "quantidade_apostas": quantidade, "dezenas_por_aposta": dezenas]
        let data = try JSONSerialization.data(withJSONObject: body)
        return try await request("/gerar-apostas", method: "POST", body: data)
    }

    // MARK: - Dashboard
    func getDashboard() async throws -> DashboardResponse {
        try await request("/admin/dashboard/summary")
    }
}

// MARK: - Models

struct TokenResponse: Codable { let access_token: String; let token_type: String }
struct FeatureResponse: Codable, Identifiable {
    var id: String { slug }
    let slug: String; let nome: String; let ativa: Bool
}
struct BetResponse: Codable { let jogo: String; let apostas: [[Int]]; let valor_total: Double }
struct DashboardResponse: Codable {
    let total_usuarios: Int; let total_apostas: Int; let total_promessas: Int
}

enum APIError: Error {
    case invalidURL, invalidResponse, httpError(Int)
}
