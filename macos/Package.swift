// swift-tools-version: 6.3
import PackageDescription

let package = Package(
    name: "Cadence",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "Cadence",
            path: "Sources/Cadence",
            exclude: ["Info.plist"]
        ),
        .testTarget(name: "CadenceTests", dependencies: ["Cadence"]),
    ]
)
