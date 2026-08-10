import XCTest
@testable import Cadence

final class MicrophoneDeviceTests: XCTestCase {
    func testDiscoveredMicrophonesHaveStableUniqueIdentifiers() {
        let microphones = MicrophoneDiscovery.availableDevices()

        XCTAssertTrue(microphones.allSatisfy { !$0.id.isEmpty && !$0.name.isEmpty })
        XCTAssertEqual(Set(microphones.map(\.id)).count, microphones.count)
    }
}
