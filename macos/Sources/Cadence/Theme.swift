import SwiftUI

enum Theme {
    static let bg = Color(.sRGB, white: 1.0, opacity: 1)
    static let surface = Color(.sRGB, red: 0.96, green: 0.97, blue: 0.98, opacity: 1)

    static let border = Color(.sRGB, red: 0.91, green: 0.92, blue: 0.93, opacity: 1)

    static let text = Color(.sRGB, red: 0.10, green: 0.11, blue: 0.13, opacity: 1)
    static let textSecondary = Color(.sRGB, red: 0.40, green: 0.43, blue: 0.47, opacity: 1)
    static let textTertiary = Color(.sRGB, red: 0.60, green: 0.63, blue: 0.66, opacity: 1)

    static let accent = Color(.sRGB, red: 0.22, green: 0.47, blue: 0.96, opacity: 1)

    static let recording = Color(.sRGB, red: 0.91, green: 0.30, blue: 0.24, opacity: 1)
    static let recordingSubtle = Color(.sRGB, red: 0.91, green: 0.30, blue: 0.24, opacity: 0.10)

    static let columnColors: [String: Color] = [
        "TODO": Color(.sRGB, red: 0.60, green: 0.63, blue: 0.68, opacity: 1),
        "IN_PROGRESS": Color(.sRGB, red: 0.22, green: 0.47, blue: 0.96, opacity: 1),
        "IN_REVIEW": Color(.sRGB, red: 0.60, green: 0.40, blue: 0.90, opacity: 1),
        "DONE": Color(.sRGB, red: 0.20, green: 0.72, blue: 0.53, opacity: 1),
    ]

    static let columnBgs: [String: Color] = [
        "TODO": Color(.sRGB, red: 0.96, green: 0.96, blue: 0.97, opacity: 1),
        "IN_PROGRESS": Color(.sRGB, red: 0.93, green: 0.95, blue: 1.0, opacity: 1),
        "IN_REVIEW": Color(.sRGB, red: 0.96, green: 0.94, blue: 1.0, opacity: 1),
        "DONE": Color(.sRGB, red: 0.93, green: 0.98, blue: 0.96, opacity: 1),
    ]

    static let popoverWidth: CGFloat = 480
    static let cardRadius: CGFloat = 5
}
