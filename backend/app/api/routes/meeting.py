import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.meeting_session import MeetingSession

router = APIRouter()
log = logging.getLogger(__name__)


@router.websocket("/ws/meeting/{meeting_id}")
async def meeting_ws(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    board = websocket.app.state.board
    session = MeetingSession(ws=websocket, board=board)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "start_recording":
                await session.start()

            elif msg_type == "stop_recording":
                await session.stop()

            elif msg_type == "audio_data":
                await session.handle_audio(data["data"])

            elif msg_type == "speaker_map":
                session.update_speaker_map(data["map"])

    except WebSocketDisconnect:
        await session.stop()
    except Exception as e:
        log.exception("WebSocket error in meeting %s: %s", meeting_id, e)
        await session.stop()
