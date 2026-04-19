import Foundation

final class WebSocketClient: @unchecked Sendable {
    private var task: URLSessionWebSocketTask?
    private let session = URLSession(configuration: .default)
    var onMessage: ((ServerMessage) -> Void)?

    func connect(meetingId: String, host: String = "localhost", port: Int = 8000) {
        let url = URL(string: "ws://\(host):\(port)/ws/meeting/\(meetingId)")!
        task = session.webSocketTask(with: url)
        task?.resume()
        receiveLoop()
    }

    func send(_ dict: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: dict),
              let text = String(data: data, encoding: .utf8) else { return }
        task?.send(.string(text)) { _ in }
    }

    func sendAudio(_ base64: String) {
        send(["type": "audio_data", "data": base64])
    }

    func disconnect() {
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
    }

    private func receiveLoop() {
        task?.receive { [weak self] result in
            switch result {
            case .success(.string(let text)):
                if let data = text.data(using: .utf8),
                   let msg = ServerMessage.parse(data) {
                    DispatchQueue.main.async { self?.onMessage?(msg) }
                }
            default:
                break
            }
            self?.receiveLoop()
        }
    }
}
