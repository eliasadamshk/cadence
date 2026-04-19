import SwiftUI

struct PopoverView: View {
    @Bindable var vm: MeetingViewModel

    var body: some View {
        VStack(spacing: 0) {
            header
                .padding(.horizontal, 20)
                .padding(.vertical, 16)

            divider

            if vm.isBoardLoading {
                HStack(spacing: 8) {
                    ProgressView()
                        .scaleEffect(0.6)
                        .frame(width: 14, height: 14)
                    Text("Loading board...")
                        .font(.system(size: 11, weight: .regular))
                        .foregroundStyle(Theme.textTertiary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 24)
            } else {
                BoardView(board: vm.board)
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                    .padding(.bottom, vm.actions.isEmpty ? 8 : 16)
            }

            if !vm.actions.isEmpty {
                divider
                actionsList
                    .padding(.horizontal, 20)
                    .padding(.vertical, 16)
            }

            if !vm.hasMicrophone {
                divider
                errorBanner("No microphone detected — connect a USB mic, headset, or AirPods.")
            } else if let err = vm.errorMessage {
                divider
                errorBanner(err)
            }

            footer
                .padding(.horizontal, 20)
                .padding(.top, 12)
                .padding(.bottom, 20)
        }
        .frame(width: Theme.popoverWidth)
        .background(Theme.bg)
    }

    private var header: some View {
        HStack(alignment: .center, spacing: 10) {
            Image(systemName: "waveform.circle.fill")
                .font(.system(size: 28, weight: .medium))
                .foregroundStyle(Theme.accent)

            Text("Cadence")
                .font(.system(size: 15, weight: .semibold, design: .default))
                .foregroundStyle(Theme.text)

            Spacer()

            if vm.isRecording {
                recordingBadge
            }
        }
    }

    private var recordingBadge: some View {
        HStack(spacing: 5) {
            Circle()
                .fill(Theme.recording)
                .frame(width: 6, height: 6)
            Text("Recording")
                .font(.system(size: 10, weight: .medium))
                .foregroundStyle(Theme.recording)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Theme.recordingSubtle)
        .clipShape(Capsule())
    }

    private var actionsList: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Recent Actions")
                .font(.system(size: 10, weight: .semibold))
                .foregroundStyle(Theme.textTertiary)
                .textCase(.uppercase)
                .tracking(0.5)
                .padding(.bottom, 2)

            ForEach(vm.actions.suffix(4)) { record in
                HStack(alignment: .top, spacing: 8) {
                    actionIcon(record.action.kind)
                        .frame(width: 16, height: 16)

                    Text(record.action.summary)
                        .font(.system(size: 11.5, weight: .regular))
                        .foregroundStyle(Theme.text)
                        .lineLimit(2)

                    Spacer(minLength: 0)

                    if record.action.kind == "MOVE_CARD", record.fromStatus != nil {
                        Image(systemName: "arrow.uturn.backward")
                            .font(.system(size: 10, weight: .medium))
                            .foregroundStyle(Theme.textSecondary)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 3)
                            .background(Theme.surface)
                            .clipShape(Capsule())
                            .onTapGesture {
                                vm.undoMove(record)
                            }
                    }
                }
                .padding(.vertical, 2)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    @ViewBuilder
    private func actionIcon(_ kind: String) -> some View {
        let (icon, color) = actionStyle(kind)
        Image(systemName: icon)
            .font(.system(size: 10, weight: .medium))
            .foregroundStyle(color)
    }

    private func actionStyle(_ kind: String) -> (String, Color) {
        switch kind {
        case "MOVE_CARD": ("arrow.right", Theme.accent)
        case "CREATE_CARD": ("plus", Color(.sRGB, red: 0.20, green: 0.72, blue: 0.53))
        case "UPDATE_CARD": ("pencil", Color(.sRGB, red: 0.60, green: 0.40, blue: 0.90))
        case "FLAG_BLOCKER": ("exclamationmark.triangle.fill", Color(.sRGB, red: 0.95, green: 0.60, blue: 0.20))
        default: ("minus", Theme.textTertiary)
        }
    }

    private func errorBanner(_ message: String) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "exclamationmark.circle.fill")
                .font(.system(size: 12))
                .foregroundStyle(Theme.recording)
            Text(message)
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(Theme.recording)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 20)
        .padding(.vertical, 10)
        .background(Theme.recordingSubtle)
    }

    private var footer: some View {
        let canStart = vm.hasMicrophone
        return HStack(spacing: 8) {
            Text(vm.isRecording ? "End" : "Start")
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(.white)
                .padding(.horizontal, 18)
                .padding(.vertical, 8)
                .background(startBackground(canStart: canStart))
                .clipShape(Capsule())
                .opacity(canStart ? 1.0 : 0.45)
                .onTapGesture {
                    guard canStart else { return }
                    if vm.isRecording { vm.stopMeeting() }
                    else { vm.startMeeting() }
                }

            if !vm.actions.isEmpty {
                Text("Restart")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 8)
                    .background(Theme.accent)
                    .clipShape(Capsule())
                    .onTapGesture {
                        vm.clearActions()
                    }
            }

            Spacer()

            Text("Quit")
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(Theme.textTertiary)
                .onTapGesture {
                    NSApp.terminate(nil)
                }
        }
    }

    private func startBackground(canStart: Bool) -> Color {
        if vm.isRecording { return Theme.recording }
        return canStart ? Theme.accent : Theme.textTertiary
    }

    private var divider: some View {
        Rectangle()
            .fill(Theme.border)
            .frame(height: 0.5)
    }
}
