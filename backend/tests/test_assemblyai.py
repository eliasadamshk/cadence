from urllib.parse import parse_qs, urlparse

import pytest

from app.services.assemblyai import AssemblyAIRealtime


async def noop(*args):
    return None


class FakeWebSocket:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration

    async def send(self, message):
        return None

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_connect_configures_low_latency_turn_detection(monkeypatch):
    captured = {}

    async def connect(url, **kwargs):
        captured["url"] = url
        return FakeWebSocket()

    monkeypatch.setattr("app.services.assemblyai.websockets.connect", connect)
    client = AssemblyAIRealtime("key", noop, noop)

    await client.connect()
    await client.close()

    params = parse_qs(urlparse(captured["url"]).query)
    assert params["min_turn_silence"] == ["100"]
    assert params["max_turn_silence"] == ["700"]


def test_turn_level_speaker_label_takes_precedence():
    client = AssemblyAIRealtime("key", noop, noop)

    assert client._extract_speaker({"speaker_label": "B", "words": [{"speaker": "A"}]}) == "B"
    assert client._extract_speaker({"words": [{"speaker": "C"}]}) == "C"
    assert client._extract_speaker({}) == "UNKNOWN"
