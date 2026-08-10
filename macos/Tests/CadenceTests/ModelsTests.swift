import XCTest
@testable import Cadence

final class ModelsTests: XCTestCase {
    func testParsesTranscriptMessages() throws {
        let partial = Data(
            #"{"type":"transcript_partial","text":"Working on OAuth","speaker":"A"}"#.utf8
        )
        let final = Data(
            #"{"type":"transcript_final","id":"u1","text":"OAuth is done.","speaker":"A","timestamp":42}"#.utf8
        )

        guard case .transcriptPartial(let text, let speaker) = ServerMessage.parse(partial) else {
            return XCTFail("Expected partial transcript")
        }
        XCTAssertEqual(text, "Working on OAuth")
        XCTAssertEqual(speaker, "A")

        guard case .transcriptFinal(let utterance) = ServerMessage.parse(final) else {
            return XCTFail("Expected final transcript")
        }
        XCTAssertEqual(utterance.id, "u1")
        XCTAssertEqual(utterance.timestamp, 42)
    }

    func testParsesBlockedCardAndMeetingStopped() throws {
        let board = Data(
            #"{"type":"board_state","board":{"columns":[{"id":"TODO","name":"Todo","cards":[{"id":"CAD-1","title":"Migration","assignee":"Jordan","blocker":"Waiting for DBA"}]}]}}"#.utf8
        )
        let stopped = Data(#"{"type":"meeting_stopped"}"#.utf8)

        guard case .boardState(let parsed) = ServerMessage.parse(board) else {
            return XCTFail("Expected board state")
        }
        XCTAssertEqual(parsed.columns[0].cards[0].blocker, "Waiting for DBA")

        guard case .meetingStopped = ServerMessage.parse(stopped) else {
            return XCTFail("Expected meeting stopped")
        }
    }
}
