import AVFoundation
import SwiftUI

struct PopoverView: View {
    @Bindable var vm: MeetingViewModel

    var body: some View {
        VStack(spacing: 0) {
            header
                .padding(.horizontal, 20)
                .padding(.vertical, 16)

            divider

            scrollableContent

            if !vm.hasMicrophone && !vm.usesFixture {
                divider
                errorBanner(
                    "No microphone detected — connect a USB mic or headset.",
                    actionTitle: "Refresh",
                    action: vm.refreshMicrophones
                )
            } else if let err = vm.errorMessage {
                divider
                errorBanner(err)
            }

            footer
                .padding(.horizontal, 20)
                .padding(.top, 12)
                .padding(.bottom, 24)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(width: Theme.popoverWidth)
        .fixedSize(horizontal: false, vertical: true)
        .background(Theme.bg)
        .onReceive(NotificationCenter.default.publisher(for: AVCaptureDevice.wasConnectedNotification)) { _ in
            vm.refreshMicrophones()
        }
        .onReceive(NotificationCenter.default.publisher(for: AVCaptureDevice.wasDisconnectedNotification)) { _ in
            vm.refreshMicrophones()
        }
    }

    private var scrollableContent: some View {
        VStack(spacing: 0) {
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

            divider

            speakerMapping
                .padding(.horizontal, 20)
                .padding(.vertical, 12)

            divider

            transcript
                .padding(.horizontal, 20)
                .padding(.vertical, 12)

            if !vm.actions.isEmpty {
                divider
                actionsList
                    .padding(.horizontal, 20)
                    .padding(.vertical, 16)
            }
        }
    }

    private var header: some View {
        HStack(alignment: .center, spacing: 10) {
            Image(systemName: "waveform.circle.fill")
                .font(.system(size: 28, weight: .medium))
                .foregroundStyle(Theme.accent)

            VStack(alignment: .leading, spacing: 1) {
                Text("Cadence")
                    .font(.system(size: 15, weight: .semibold, design: .default))
                    .foregroundStyle(Theme.text)
                Text("Live standup sync")
                    .font(.system(size: 11, weight: .regular))
                    .foregroundStyle(Theme.textTertiary)
            }

            Spacer()

            if !vm.usesFixture {
                microphoneMenu
            }

            if vm.isRecording || vm.isConnecting || vm.isStopping {
                sessionBadge
            }
        }
    }

    private var microphoneMenu: some View {
        Menu {
            if vm.microphones.isEmpty {
                Text("No microphones found")
            } else {
                ForEach(vm.microphones) { microphone in
                    Button {
                        vm.selectMicrophone(microphone.id)
                    } label: {
                        if microphone.id == vm.selectedMicrophoneID {
                            Label(microphone.name, systemImage: "checkmark")
                        } else {
                            Text(microphone.name)
                        }
                    }
                }
            }

            Divider()

            Button {
                vm.refreshMicrophones()
            } label: {
                Label("Refresh Devices", systemImage: "arrow.clockwise")
            }
        } label: {
            HStack(spacing: 5) {
                Image(systemName: "mic.fill")
                Text(vm.selectedMicrophoneName)
                    .lineLimit(1)
                    .truncationMode(.tail)
                    .frame(maxWidth: 140, alignment: .trailing)
                Image(systemName: "chevron.down")
                    .font(.system(size: 7, weight: .semibold))
            }
            .font(.system(size: 10, weight: .medium))
            .foregroundStyle(Theme.textSecondary)
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .background(Theme.surface)
            .clipShape(Capsule())
        }
        .menuStyle(.borderlessButton)
        .fixedSize()
        .disabled(vm.isRecording || vm.isConnecting || vm.isStopping)
    }

    private var sessionBadge: some View {
        HStack(spacing: 5) {
            Circle()
                .fill(vm.isRecording ? Theme.recording : Theme.accent)
                .frame(width: 6, height: 6)
            Text(vm.isConnecting ? "Connecting" : vm.isStopping ? "Finishing" : "Recording")
                .font(.system(size: 10, weight: .medium))
                .foregroundStyle(vm.isRecording ? Theme.recording : Theme.accent)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(vm.isRecording ? Theme.recordingSubtle : Theme.surface)
        .clipShape(Capsule())
    }

    private var speakerMapping: some View {
        VStack(alignment: .leading, spacing: 7) {
            sectionTitle("Speakers")
            HStack(spacing: 8) {
                ForEach(["A", "B", "C", "D"], id: \.self) { label in
                    VStack(alignment: .leading, spacing: 3) {
                        Text(label)
                            .font(.system(size: 9, weight: .semibold, design: .monospaced))
                            .foregroundStyle(Theme.textTertiary)
                        TextField(
                            "Name",
                            text: Binding(
                                get: { vm.speakerNames[label] ?? "" },
                                set: { vm.updateSpeakerName(label, name: $0) }
                            )
                        )
                        .textFieldStyle(.roundedBorder)
                        .font(.system(size: 10))
                    }
                }
            }
        }
    }

    private var transcript: some View {
        VStack(alignment: .leading, spacing: 7) {
            sectionTitle("Live Transcript")
            VStack(alignment: .leading, spacing: 6) {
                if vm.utterances.isEmpty && vm.partialText == nil {
                    Text("Transcript will appear when recording starts.")
                        .font(.system(size: 10.5))
                        .foregroundStyle(Theme.textTertiary)
                }

                ForEach(vm.utterances) { utterance in
                    transcriptLine(
                        speaker: utterance.speaker,
                        text: utterance.text,
                        isPartial: false
                    )
                }

                if let partial = vm.partialText {
                    transcriptLine(
                        speaker: vm.partialSpeaker ?? "UNKNOWN",
                        text: partial,
                        isPartial: true
                    )
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func transcriptLine(speaker: String, text: String, isPartial: Bool) -> some View {
        HStack(alignment: .top, spacing: 7) {
            Text(vm.displayName(for: speaker))
                .font(.system(size: 9.5, weight: .semibold))
                .foregroundStyle(Theme.accent)
                .frame(width: 72, alignment: .leading)
                .lineLimit(1)
            Text(text)
                .font(.system(size: 10.5))
                .foregroundStyle(isPartial ? Theme.textTertiary : Theme.text)
                .italic(isPartial)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func sectionTitle(_ title: String) -> some View {
        Text(title)
            .font(.system(size: 10, weight: .semibold))
            .foregroundStyle(Theme.textTertiary)
            .textCase(.uppercase)
            .tracking(0.5)
    }

    private var actionsList: some View {
        VStack(alignment: .leading, spacing: 6) {
            sectionTitle("Recent Actions")
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

    private func errorBanner(
        _ message: String,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil
    ) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "exclamationmark.circle.fill")
                .font(.system(size: 12))
                .foregroundStyle(Theme.recording)
            Text(message)
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(Theme.recording)
                .lineLimit(2)

            Spacer(minLength: 8)

            if let actionTitle, let action {
                Button(actionTitle, action: action)
                    .buttonStyle(.plain)
                    .font(.system(size: 10.5, weight: .semibold))
                    .foregroundStyle(Theme.recording)
                    .padding(.horizontal, 9)
                    .padding(.vertical, 5)
                    .background(Theme.bg.opacity(0.8))
                    .clipShape(Capsule())
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 20)
        .padding(.vertical, 10)
        .background(Theme.recordingSubtle)
    }

    private var footer: some View {
        let canStart =
            (vm.hasMicrophone || vm.usesFixture) && !vm.isConnecting && !vm.isStopping
        return HStack(spacing: 8) {
            Text(
                vm.isConnecting
                    ? "Connecting…" : vm.isStopping ? "Finishing…" : vm.isRecording ? "End" : "Start"
            )
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(.white)
                .padding(.horizontal, 18)
                .padding(.vertical, 8)
                .background(startBackground(canStart: canStart))
                .clipShape(Capsule())
                .opacity(canStart ? 1.0 : 0.45)
                .onTapGesture {
                    guard canStart else { return }
                    if vm.isRecording {
                        vm.stopMeeting()
                    } else {
                        vm.startMeeting()
                    }
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
