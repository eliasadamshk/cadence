from fastapi.testclient import TestClient

from app.main import app


def test_health_and_seeded_board():
    with TestClient(app) as client:
        health = client.get("/health")
        board = client.get("/v1/board")
        legacy_board = client.get("/api/board")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert board.status_code == 200
    assert legacy_board.status_code == 404
    assert len(board.json()["columns"]) == 4
    assert sum(len(column["cards"]) for column in board.json()["columns"]) == 8


def test_move_card_validates_status_and_missing_card():
    with TestClient(app) as client:
        invalid = client.post("/v1/board/cards/CAD-1/move", json={"to_status": "INVALID"})
        missing = client.post("/v1/board/cards/CAD-999/move", json={"to_status": "DONE"})

    assert invalid.status_code == 422
    assert missing.status_code == 404
