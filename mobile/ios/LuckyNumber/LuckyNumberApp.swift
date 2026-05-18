// LuckyNumberApp.swift
// Lucky Number iOS app — SwiftUI
// Prevents CWE-522: Keychain storage, never UserDefaults
// Versão mínima: iOS 15.0 (95% cobertura Brasil)

import SwiftUI

@main
struct LuckyNumberApp: App {
    @StateObject private var authViewModel = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel)
                .preferredColorScheme(.none)  // Follow system dark/light
        }
    }
}
