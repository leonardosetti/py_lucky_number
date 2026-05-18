import SwiftUI

struct GenerateView: View {
    @State private var jogo = "megasena"
    @State private var quantidade = 1
    @State private var dezenas = 6
    @State private var result: BetResponse? = nil
    let games = ["megasena", "lotofacil", "quina", "duplasena", "diadesorte"]

    var body: some View {
        NavigationView {
            Form {
                Picker("Jogo", selection: $jogo) {
                    ForEach(games, id: \.self) { Text($0) }
                }
                Stepper("Quantidade: \(quantidade)", value: $quantidade, in: 1...10)
                Stepper("Dezenas: \(dezenas)", value: $dezenas, in: 6...20)

                Button("Gerar") { Task { await generate() } }
                    .buttonStyle(.borderedProminent).frame(maxWidth: .infinity)

                if let r = result {
                    Section("Resultado") {
                        Text("Total: R$ \(r.valor_total, specifier: "%.2f")")
                        ForEach(Array(r.apostas.enumerated()), id: \.offset) { i, nums in
                            Text(nums.map { String(format: "%02d", $0) }.joined(separator: " - "))
                                .font(.caption).swipeActions { Button("Excluir", role: .destructive) {} }
                        }
                    }
                }
            }
            .navigationTitle("Gerar Apostas")
        }
    }

    func generate() async {
        result = try? await APIClient.shared.gerarApostas(jogo: jogo, quantidade: quantidade, dezenas: dezenas)
    }
}
