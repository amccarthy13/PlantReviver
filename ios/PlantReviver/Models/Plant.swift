import Foundation
import SwiftData

/// Local source of truth for a plant. Carries the same syncable fields as the
/// backend (`id`, `updatedAt`, `deletedAt`) so offline-first sync can reconcile
/// (ARCHITECTURE.md §11).
@Model
final class Plant {
    @Attribute(.unique) var id: UUID
    var name: String
    var wateringIntervalDays: Int?
    var lastWateredAt: Date?
    var nextWateringDate: Date?
    var notes: String

    var createdAt: Date
    var updatedAt: Date
    var deletedAt: Date?

    init(
        id: UUID = UUID(),
        name: String,
        wateringIntervalDays: Int? = nil,
        notes: String = ""
    ) {
        self.id = id
        self.name = name
        self.wateringIntervalDays = wateringIntervalDays
        self.notes = notes
        let now = Date()
        self.createdAt = now
        self.updatedAt = now
    }
}
