.PHONY: dev backend frontend setup lint mac

dev:
	$(MAKE) -j2 backend frontend

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && pnpm dev

setup:
	cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e . --group eval --group dev
	cd frontend && pnpm install

lint:
	cd backend && source .venv/bin/activate && ruff check . && ruff format --check .
	cd frontend && pnpm exec biome check .

eval-fast:
	cd backend && source .venv/bin/activate && python -m evals.runner fast

eval-e2e:
	cd backend && source .venv/bin/activate && python -m evals.runner e2e

mac:
	cd macos && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift build -c release
	rm -rf macos/.build/release/Cadence.app
	mkdir -p macos/.build/release/Cadence.app/Contents/MacOS macos/.build/release/Cadence.app/Contents/Resources
	cp macos/.build/release/Cadence macos/.build/release/Cadence.app/Contents/MacOS/Cadence
	cp macos/Sources/Cadence/Info.plist macos/.build/release/Cadence.app/Contents/
	printf 'APPL????' > macos/.build/release/Cadence.app/Contents/PkgInfo
	codesign --force --deep --sign - macos/.build/release/Cadence.app
	open macos/.build/release/Cadence.app

eval-generate:
	cd backend && source .venv/bin/activate && python -m evals.generate_audio

# Wire the Mac app to replay a WAV fixture instead of opening the microphone.
# Usage: make mac-mock FIXTURE=backend/evals/fixtures/simple_updates.wav
mac-mock:
	@test -n "$(FIXTURE)" || (echo "Usage: make mac-mock FIXTURE=path/to/file.wav"; exit 1)
	@test -f "$(FIXTURE)" || (echo "Fixture not found: $(FIXTURE)"; exit 1)
	defaults write com.cadence.app CADENCE_MOCK_AUDIO -string "$(abspath $(FIXTURE))"
	@echo "Mock audio set to $(abspath $(FIXTURE)). Run 'make mac' to launch."

mac-unmock:
	defaults delete com.cadence.app CADENCE_MOCK_AUDIO 2>/dev/null || true
	@echo "Mock audio cleared. App will use the live microphone."
