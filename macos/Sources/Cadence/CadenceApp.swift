import SwiftUI

@main
struct CadenceApp: App {
    @State private var vm = MeetingViewModel()

    var body: some Scene {
        MenuBarExtra {
            PopoverView(vm: vm)
                .environment(\.colorScheme, .light)
        } label: {
            Image(systemName: "waveform.circle.fill")
        }
        .menuBarExtraStyle(.window)
    }
}
