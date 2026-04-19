# cadence

Live standup meetings that update your board automatically.

## What is this?

At a London tech event, someone mentioned that their team never interacts with their board anymore. Standups somehow update everything automatically. They didn't go into detail on how it works, just that it does. They also mentioned using [Granola](https://granola.ai) for meeting notes.

That was enough to get the wheels turning. Cadence is my interpretation of what that could look like: a tool that listens to your standup, transcribes it in real-time with speaker identification, and extracts project management actions (moving cards, creating tickets, flagging blockers) as people talk.

The project management layer is deliberately abstract. It's mocked with an in-memory board for now, but the interface is designed so you can plug in Jira, Linear, or whatever your team uses.

## How it works

```
Mic → Mac app (16kHz PCM16) → WebSocket → Backend
                                             │
                               ┌─────────────┤
                               ▼             ▼
                       AssemblyAI WS    TranscriptBuffer
                       (real-time +     (flushes every ~30s)
                        diarization)         │
                               │             ▼
                               ▼         OpenRouter → Gemini
                       Live transcript   Flash Lite
                               │             │
                               ▼             ▼
                         Mac app UI     Parse actions → Board
```

Two independent pipelines share a single WebSocket connection to the Mac app:

1. **Transcript pipeline**: immediate. Partial and final results from AssemblyAI stream directly to the UI.
2. **Action pipeline**: buffered. Finalized utterances accumulate and flush to the LLM every ~30 seconds or on speaker change. The LLM extracts structured actions and the board updates.

## Tech stack

- **Backend**: Python, FastAPI, raw WebSockets
- **Mac app**: SwiftUI, native menu bar app
- **Transcription**: AssemblyAI real-time WebSocket API (with speaker diarization)
- **LLM**: Gemini 3.1 Flash Lite Preview via OpenRouter
- **Board**: Abstract `ProjectBoard` interface, in-memory mock for dev

## Setup

```bash
# Clone and install
git clone <repo-url>
cd cadence
cp .env.example .env
# Add your ASSEMBLYAI_API_KEY and OPENROUTER_API_KEY to .env

make setup
```

## Running

```bash
# Start the backend
make dev

# Or with Docker
docker compose up
```

Then open the Cadence Mac app from the menu bar.

## Usage

1. Map speaker names in the settings (Speaker A = Sarah, etc.)
2. Click **Start Recording** and grant microphone access
3. Talk through a standup: "I finished the OAuth login, moving it to review. Today I'm picking up the rate limiting ticket."
4. Watch the transcript appear live
5. Watch cards move on the board

## Project structure

```
cadence/
├── backend/
│   └── app/
│       ├── api/routes/       # HTTP + WebSocket endpoints
│       ├── services/         # AssemblyAI, LLM, buffer, session orchestrator
│       ├── models/           # Pydantic models for messages, board, actions
│       └── pm/               # Abstract ProjectBoard + InMemoryBoard
├── macos/
│   └── Sources/Cadence/      # SwiftUI menu bar app
├── docker-compose.yml
└── Makefile
```

## Linting

```bash
make lint
```

Uses ruff for Python.

## Contributing

Welcome all ideas and contributions. Open an issue or submit a PR.
