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
                       (real-time +      (flushes every ~5s)
                        diarization)         │
                               │             ▼
                               ▼         OpenRouter → Gemini
                       Live transcript   Flash Lite (GA)
                               │             │
                               ▼             ▼
                         Mac app UI     Parse actions → Board
```

Two independent pipelines share a single WebSocket connection to the Mac app:

1. **Transcript pipeline**: immediate. Partial and final results from AssemblyAI stream directly to the UI.
2. **Action pipeline**: buffered. Finalized utterances accumulate and flush to the LLM every ~5 seconds and when the meeting ends. The LLM extracts schema-validated actions and the board updates.

## Tech stack

- **Backend**: Python, FastAPI, raw WebSockets
- **Mac app**: SwiftUI, native menu bar app
- **Transcription**: AssemblyAI real-time WebSocket API (with speaker diarization)
- **LLM**: Gemini 3.1 Flash Lite via OpenRouter structured outputs
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
# Start the backend, then launch the native app
make dev
make mac

# Or with Docker
docker compose up
```

Cadence appears in the macOS menu bar.

## Usage

1. Map speaker labels to names in the menu-bar popover (Speaker A = Sarah, etc.)
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
├── .github/workflows/ci.yml  # Backend and macOS verification
├── docker-compose.yml
└── Makefile
```

## Verification

```bash
make verify
```

This runs Ruff, the backend test suite, Swift tests, and a native Swift build. The live evals require AssemblyAI and OpenRouter API keys and are intentionally separate.

## Contributing

Welcome all ideas and contributions. Open an issue or submit a PR.
