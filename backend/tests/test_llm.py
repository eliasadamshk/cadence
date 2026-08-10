import json

import pytest

from app.services.llm import extract_actions


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "actions": [
                                    {
                                        "kind": "MOVE_CARD",
                                        "card_id": "CAD-1",
                                        "title": None,
                                        "assignee": None,
                                        "to_status": "IN_REVIEW",
                                        "summary": "OAuth moved to review",
                                        "source_text": "OAuth is ready for review",
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        }


class FakeClient:
    request = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def post(self, url, **kwargs):
        FakeClient.request = (url, kwargs)
        return FakeResponse()


@pytest.mark.asyncio
async def test_extract_actions_requests_and_validates_structured_output(monkeypatch):
    monkeypatch.setattr("app.services.llm.httpx2.AsyncClient", FakeClient)
    board = json.dumps({"columns": []})

    actions = await extract_actions(
        transcript_segment="[Sarah]: OAuth is ready for review.",
        previous_context="",
        board_state_json=board,
        speaker_map={"A": "Sarah"},
        api_key="test-key",
        model="test-model",
    )

    assert actions[0].card_id == "CAD-1"
    assert actions[0].to_status == "IN_REVIEW"
    payload = FakeClient.request[1]["json"]
    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["provider"] == {
        "require_parameters": True,
        "sort": "latency",
    }
