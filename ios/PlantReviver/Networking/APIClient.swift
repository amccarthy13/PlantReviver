import Foundation

/// Thin async client for the FastAPI backend. Auth is a bearer JWT obtained via
/// Sign in with Apple (ARCHITECTURE.md §6).
actor APIClient {
    private let baseURL: URL
    private var accessToken: String?

    init(baseURL: URL) {
        self.baseURL = baseURL
    }

    func setAccessToken(_ token: String?) {
        accessToken = token
    }

    // TODO: generic request helper, /auth/apple, /sync/changes, /sync/push.
}
