import SwiftUI

struct CadenceLogo: View {
    let isActive: Bool
    let size: CGFloat
    var weight: Font.Weight = .medium

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Image(systemName: "waveform.circle.fill")
            .font(.system(size: size, weight: weight))
            .symbolEffect(
                .variableColor.iterative.reversing,
                options: .repeating,
                isActive: isActive && !reduceMotion
            )
            .accessibilityLabel("Cadence")
    }
}
