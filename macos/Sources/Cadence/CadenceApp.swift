import SwiftUI

@main
struct CadenceApp: App {
    @State private var vm = MeetingViewModel()

    var body: some Scene {
        MenuBarExtra {
            PopoverView(vm: vm)
                .environment(\.colorScheme, .light)
        } label: {
            CadenceLogo(isActive: vm.isRecording, size: 16, weight: .semibold)
        }
        .menuBarExtraStyle(.window)
    }
}
