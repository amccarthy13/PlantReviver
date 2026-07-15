import SwiftData
import SwiftUI

@main
struct PlantReviverApp: App {
    var body: some Scene {
        WindowGroup {
            PlantListView()
        }
        .modelContainer(for: [Plant.self])
    }
}
