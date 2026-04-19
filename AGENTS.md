# Agents

## Code Style

- Only add comments where the logic isn't self-evident. No obvious or redundant comments.
- Don't be overly defensive. No unnecessary try/catch, validation for impossible states, or error handling for internal code. Only validate at system boundaries (user input, external APIs).
- Don't add features, refactor code, or make "improvements" beyond what was asked.

## Tooling

- **Python**: Use ruff for linting and formatting. Config in `backend/ruff.toml`.
- **Swift**: macOS app uses SwiftUI. Xcode project in `macos/`.

## Project Conventions

- Backend uses FastAPI with Pydantic models. Keep routes thin. Business logic lives in `services/`.
- macOS app is a native SwiftUI menu bar app that captures audio and communicates with the backend.
- WebSocket message protocol uses a `type` field discriminator. All message types defined in `backend/app/models/messages.py`.
- The project management layer is abstract (`pm/base.py`). The in-memory implementation is for development. Don't hardcode Jira/Linear specifics anywhere outside of a concrete `ProjectBoard` implementation.

## Git

- Don't push to remote unless explicitly asked.
- Don't amend commits unless explicitly asked.
