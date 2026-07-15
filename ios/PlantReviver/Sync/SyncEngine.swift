import Foundation
import SwiftData

/// Offline-first sync engine (ARCHITECTURE.md §11).
///
/// Responsibilities (to implement in build-order step 4):
///  - pull `/sync/changes?since=<cursor>` and apply remote rows (incl. tombstones)
///  - flush the local outbox to `/sync/push` (idempotent, keyed by client UUID)
///  - trigger on foreground, on regained connectivity, and periodically
actor SyncEngine {
    private let api: APIClient

    init(api: APIClient) {
        self.api = api
    }

    func sync() async throws {
        // TODO: implement pull + push reconciliation.
    }
}
