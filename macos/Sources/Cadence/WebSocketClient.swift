@preconcurrency import Foundation

final class WebSocketClient: NSObject, URLSessionWebSocketDelegate, @unchecked Sendable {
    private var task: URLSessionWebSocketTask?
    private lazy var session = URLSession(
        configuration: .default,
        delegate: self,
        delegateQueue: nil
    )
    var onConnected: (() -> Void)?
    var onDisconnected: ((String?) -> Void)?
    var onMessage: ((ServerMessage) -> Void)?

    func connect(meetingId: String, host: String = "localhost", port: Int = 8000) {
        let url = URL(string: "ws://\(host):\(port)/ws/meeting/\(meetingId)")!
        task = session.webSocketTask(with: url)
        task?.resume()
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

    func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didOpenWithProtocol protocol: String?
    ) {
        DispatchQueue.main.async { [weak self] in
            self?.onConnected?()
        }
        receiveLoop()
    }

    func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
        reason: Data?
    ) {
        DispatchQueue.main.async { [weak self] in
            self?.onDisconnected?(nil)
        }
    }

    private func receiveLoop() {
        task?.receive { [weak self] result in
            switch result {
            case .success(.string(let text)):
                if let data = text.data(using: .utf8),
                   let msg = ServerMessage.parse(data) {
                    DispatchQueue.main.async { self?.onMessage?(msg) }
                }
                self?.receiveLoop()
            case .success:
                self?.receiveLoop()
            case .failure(let error):
                DispatchQueue.main.async {
                    self?.onDisconnected?(error.localizedDescription)
                }
            }
        }
    }
}
