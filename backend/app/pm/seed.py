from __future__ import annotations

from app.pm.memory import InMemoryBoard

SEED_TICKETS = [
    ("Add OAuth2 login flow", "Sarah", "IN_PROGRESS"),
    ("Fix payment webhook retry logic", "Marcus", "IN_REVIEW"),
    ("Update dashboard chart colors", "Sarah", "TODO"),
    ("Write API rate limiting middleware", None, "TODO"),
    ("Migrate user table to new schema", "Jordan", "IN_PROGRESS"),
    ("Add email notification templates", "Marcus", "DONE"),
    ("Set up staging environment", "Jordan", "IN_REVIEW"),
    ("Create onboarding tooltip tour", None, "TODO"),
]


def seed_board() -> InMemoryBoard:
    board = InMemoryBoard()
    for title, assignee, status in SEED_TICKETS:
        board._add(title, assignee, status)
    return board
