# Contributing to CADENCE

Thanks for your interest. Cadence is open to contributions of any size: bug reports, docs, tests, features, or whole new board adapters. No contribution is too small.

## Ways to contribute

- **Bug reports**: open an issue with steps to reproduce, expected vs. actual behavior, and backend logs if relevant.
- **Feature ideas**: open an issue first so we can discuss shape before you write code.
- **Pull requests**: small, focused changes are easiest to review. See below.
- **Board adapters**: probably the most valuable thing you can add. See [Adding a board adapter](#adding-a-board-adapter).
- **Docs**: the README is short on purpose, but fixes and clarifications are welcome.

## Dev setup

Start with the [README](README.md) for the full setup. You'll need:

- Python 3.11+
- Xcode 15+ (for the Mac app)
- `make`
- An [AssemblyAI](https://www.assemblyai.com) API key and an [OpenRouter](https://openrouter.ai) API key.

```bash
git clone https://github.com/eliasadamshk/cadence
cd cadence
cp .env.example .env    # add your API keys
make setup
make dev
```

## Running & testing

```bash
make dev     # start the backend
make lint    # ruff
```

Eval suite lives alongside the backend. Run it before submitting changes to the LLM prompt or action-parsing logic so regressions are caught early.

## Architecture tour

Two pipelines share one WebSocket connection to the Mac app (full diagram in the README):

- **Transcript pipeline**: [backend/app/services](backend/app/services) streams AssemblyAI results straight to the UI.
- **Action pipeline**: a [TranscriptBuffer](backend/app/services) flushes finalized utterances to the LLM every ~30s; the parsed actions mutate the board.

If you're touching prompts, they live with the LLM service. If you're touching the board, see below.

## Adding a board adapter

The `ProjectBoard` interface in [backend/app/pm](backend/app/pm) is the extension point. To add Jira, Linear, GitHub Projects, or anything else:

1. Create a new module under `backend/app/pm/` that implements `ProjectBoard`.
2. Wire it up via env-var config so users can switch without code changes.
3. Add an integration test that exercises the full flow (transcript → action → board mutation) against either a real sandbox or a recorded fixture.
4. Document the required env vars in `.env.example`.

Keep the adapter dumb. Action parsing and prompt logic stay in the backend; adapters translate structured actions into board API calls, nothing more.

## Commit & PR guidelines

- One logical change per PR. If you find unrelated cleanup while you're in there, make it a second PR.
- Commit messages: present tense, imperative mood (`add linear adapter`, not `added` / `adds`).
- Describe *why* in the PR body, not just *what*. The diff shows what.
- Run `make lint` before pushing.
- Don't commit `.env`, API keys, recordings, or transcripts with real names.

## Reporting bugs & security

- **Bugs**: GitHub issues. Scrub any real names, audio, or transcripts before attaching logs.
- **Security issues**: please don't open a public issue. Email the maintainer directly (see the GitHub profile).

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
