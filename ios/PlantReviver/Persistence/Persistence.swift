import Foundation
import SwiftData

/// Central place to build the SwiftData container. Kept separate so tests and
/// previews can request an in-memory store.
enum Persistence {
    static let schema = Schema([Plant.self])

    static func container(inMemory: Bool = false) throws -> ModelContainer {
        let config = ModelConfiguration(schema: schema, isStoredInMemoryOnly: inMemory)
        return try ModelContainer(for: schema, configurations: [config])
    }
}
