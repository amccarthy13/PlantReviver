import SwiftData
import SwiftUI

struct PlantListView: View {
    @Environment(\.modelContext) private var context
    // Only show non-tombstoned plants (offline-first soft deletes).
    @Query(filter: #Predicate<Plant> { $0.deletedAt == nil },
           sort: \Plant.nextWateringDate)
    private var plants: [Plant]

    var body: some View {
        NavigationStack {
            List(plants) { plant in
                VStack(alignment: .leading, spacing: 2) {
                    Text(plant.name).font(.headline)
                    if let next = plant.nextWateringDate {
                        Text("Next: \(next.formatted(date: .abbreviated, time: .omitted))")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("PlantReviver")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        context.insert(Plant(name: "New Plant"))
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
        }
    }
}

#Preview {
    PlantListView()
        .modelContainer(for: [Plant.self], inMemory: true)
}
