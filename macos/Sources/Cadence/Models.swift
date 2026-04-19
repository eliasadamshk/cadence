import Foundation

struct Card: Identifiable, Codable {
    let id: String
    let title: String
    let assignee: String?
}

struct Column: Identifiable, Codable {
    let id: String
    let name: String
    let cards: [Card]
}

struct Board: Codable {
    let columns: [Column]
}

struct ExtractedAction: Codable {
    let kind: String
    let cardId: String?
    let title: String?
    let assignee: String?
    let toStatus: String?
    let summary: String
    let sourceText: String

    enum CodingKeys: String, CodingKey {
        case kind
        case cardId = "card_id"
        case title, assignee
        case toStatus = "to_status"
        case summary
        case sourceText = "source_text"
    }
}

struct ActionRecord: Identifiable {
    let id = UUID()
    let action: ExtractedAction
    let fromStatus: String?
}

enum ServerMessage {
    case boardState(Board)
    case actionExtracted(ExtractedAction)
    case error(String)

    static func parse(_ data: Data) -> ServerMessage? {
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else { return nil }

        let decoder = JSONDecoder()

        switch type {
        case "board_state":
            guard let boardData = try? JSONSerialization.data(withJSONObject: json["board"] as Any),
                  let board = try? decoder.decode(Board.self, from: boardData) else { return nil }
            return .boardState(board)

        case "action_extracted":
            guard let actionData = try? JSONSerialization.data(withJSONObject: json["action"] as Any),
                  let action = try? decoder.decode(ExtractedAction.self, from: actionData) else { return nil }
            return .actionExtracted(action)

        case "error":
            return .error(json["message"] as? String ?? "Unknown error")

        default:
            return nil
        }
    }
}
