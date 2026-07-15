# PlantReviver — iOS

SwiftUI app with a SwiftData local store as the **source of truth**, syncing to
the backend offline-first (repo `ARCHITECTURE.md` §11).

## Requirements
- Xcode 16+
- iOS 17+ (SwiftData)

## Project setup

The Xcode project file (`.xcodeproj`) is **not** checked in yet — these are the
starter Swift sources laid out by responsibility. To start developing:

1. In Xcode: **File → New → Project → App** (SwiftUI, SwiftData), name it
   `PlantReviver`, and add the files under `PlantReviver/` to the target, or
2. Point a new project at this `PlantReviver/` source folder.

(If you'd like reproducible project generation, we can add
[XcodeGen](https://github.com/yonaskolb/XcodeGen) or a Swift Package later.)

## Layout

```
PlantReviver/
  App/            app entry point
  Models/         SwiftData @Model types (mirror the backend's syncable fields)
  Views/          SwiftUI views
  Persistence/    ModelContainer configuration
  Networking/     APIClient (talks to the FastAPI backend)
  Sync/           offline-first sync engine + outbox
```
