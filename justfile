set shell := ["bash", "-cu"]

default: backend

backend:
    cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

alias dev := backend

setup:
    python3 -m venv backend/.venv
    cd backend && .venv/bin/pip install -e . --group eval --group dev

lint:
    cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .

test:
    cd backend && .venv/bin/pytest
    cd macos && swift test

verify: lint test
    cd macos && swift build

eval-fast:
    cd backend && .venv/bin/python -m evals.runner fast

eval-e2e:
    cd backend && .venv/bin/python -m evals.runner e2e

eval-generate:
    cd backend && .venv/bin/python -m evals.generate_audio

mac:
    cd macos && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift build -c release
    rm -rf macos/.build/release/Cadence.app
    mkdir -p macos/.build/release/Cadence.app/Contents/MacOS macos/.build/release/Cadence.app/Contents/Resources
    cp macos/.build/release/Cadence macos/.build/release/Cadence.app/Contents/MacOS/Cadence
    cp macos/Sources/Cadence/Info.plist macos/.build/release/Cadence.app/Contents/
    printf 'APPL????' > macos/.build/release/Cadence.app/Contents/PkgInfo
    codesign --force --deep --sign - macos/.build/release/Cadence.app
    open macos/.build/release/Cadence.app

# Wire the Mac app to replay a WAV fixture instead of opening the microphone.
mac-mock fixture:
    test -f "{{ fixture }}" || (echo "Fixture not found: {{ fixture }}"; exit 1)
    fixture_path="$(cd "$(dirname "{{ fixture }}")" && pwd)/$(basename "{{ fixture }}")"; defaults write com.cadence.app CADENCE_MOCK_AUDIO -string "$fixture_path"; echo "Mock audio set to $fixture_path. Run 'just mac' to launch."

mac-unmock:
    defaults delete com.cadence.app CADENCE_MOCK_AUDIO 2>/dev/null || true
    @echo "Mock audio cleared. App will use the live microphone."
