import AVFoundation
import SwiftUI

@MainActor @Observable
final class MeetingViewModel {
    var board = Board(columns: [
        Column(id: "TODO", name: "Todo", cards: []),
        Column(id: "IN_PROGRESS", name: "In Progress", cards: []),
        Column(id: "IN_REVIEW", name: "In Review", cards: []),
        Column(id: "DONE", name: "Done", cards: []),
    ])
    var actions: [ActionRecord] = []
    var isRecording = false
    var isBoardLoading = true
    var errorMessage: String?
    var hasMicrophone: Bool = AVCaptureDevice.default(for: .audio) != nil
    let usesFixture: Bool

    private let ws = WebSocketClient()
    private let audio: AudioSource
    private var autoStopTask: Task<Void, Never>?
    private let maxDuration: TimeInterval = 15 * 60

    init() {
        if let path = UserDefaults.standard.string(forKey: "CADENCE_MOCK_AUDIO"),
           !path.isEmpty,
           FileManager.default.fileExists(atPath: path) {
            self.audio = FixtureAudioPlayer(path: path)
            self.usesFixture = true
        } else {
            self.audio = AudioCapture()
            self.usesFixture = false
        }

        let vm = self
        ws.onMessage = { msg in
            Task { @MainActor in vm.handle(msg) }
        }
        audio.onAudioChunk = { chunk in
            vm.ws.sendAudio(chunk)
        }
        fetchBoard()
    }

    private func fetchBoard() {
        isBoardLoading = true
        Task { @MainActor in
            defer { isBoardLoading = false }
            guard let url = URL(string: "http://localhost:8000/api/board") else { return }
            do {
                let (data, _) = try await URLSession.shared.data(from: url)
                let decoded = try JSONDecoder().decode(Board.self, from: data)
                self.board = decoded
            } catch {
                // Backend unreachable — keep default empty board.
            }
        }
    }

    func startMeeting() {
        errorMessage = nil

        if usesFixture {
            beginSession()
            return
        }

        hasMicrophone = AVCaptureDevice.default(for: .audio) != nil
        guard hasMicrophone else {
            errorMessage = "No microphone detected — connect a USB mic, headset, or AirPods."
            return
        }

        let status = AVCaptureDevice.authorizationStatus(for: .audio)
        switch status {
        case .authorized:
            beginSession()
        case .notDetermined:
            Task { @MainActor in
                let granted = await AVCaptureDevice.requestAccess(for: .audio)
                if granted {
                    try? await Task.sleep(for: .milliseconds(300))
                    hasMicrophone = AVCaptureDevice.default(for: .audio) != nil
                    beginSession()
                } else {
                    errorMessage = "Microphone access denied — enable in System Settings > Privacy > Microphone"
                }
            }
        case .denied, .restricted:
            errorMessage = "Microphone access denied — enable in System Settings > Privacy > Microphone"
        @unknown default:
            errorMessage = "Microphone access unavailable"
        }
    }

    func clearActions() {
        actions.removeAll()
    }

    func undoMove(_ record: ActionRecord) {
        guard record.action.kind == "MOVE_CARD",
              let cardId = record.action.cardId,
              let fromStatus = record.fromStatus,
              let url = URL(string: "http://localhost:8000/api/board/cards/\(cardId)/move") else { return }

        Task { @MainActor in
            var req = URLRequest(url: url)
            req.httpMethod = "POST"
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = try? JSONSerialization.data(withJSONObject: ["to_status": fromStatus])

            do {
                let (data, response) = try await URLSession.shared.data(for: req)
                guard (response as? HTTPURLResponse)?.statusCode == 200 else {
                    errorMessage = "Undo failed"
                    return
                }
                if let decoded = try? JSONDecoder().decode(Board.self, from: data) {
                    board = decoded
                }
                actions.removeAll { $0.id == record.id }
            } catch {
                errorMessage = "Undo failed: \(error.localizedDescription)"
            }
        }
    }

    func stopMeeting() {
        autoStopTask?.cancel()
        autoStopTask = nil
        ws.send(["type": "stop_recording"])
        audio.stop()
        ws.disconnect()
        isRecording = false
    }

    private func beginSession() {
        let id = UUID().uuidString.prefix(8).lowercased()
        ws.connect(meetingId: String(id))
        ws.send(["type": "start_recording"])

        do {
            try audio.start()
            isRecording = true
            autoStopTask = Task { @MainActor in
                try? await Task.sleep(for: .seconds(maxDuration))
                if isRecording { stopMeeting() }
            }
        } catch {
            errorMessage = error.localizedDescription
            ws.disconnect()
        }
    }

    private func handle(_ msg: ServerMessage) {
        switch msg {
        case .boardState(let board):
            self.board = board

        case .actionExtracted(let action):
            // Snapshot current status before the follow-up board_state applies the move, so undo works.
            let from: String?
            if action.kind == "MOVE_CARD", let cardId = action.cardId {
                from = board.columns.first(where: { $0.cards.contains(where: { $0.id == cardId }) })?.id
            } else {
                from = nil
            }
            actions.append(ActionRecord(action: action, fromStatus: from))

        case .error(let message):
            errorMessage = message
        }
    }
}
