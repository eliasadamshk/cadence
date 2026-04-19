from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="blockers",
    description="Speaker reports being blocked, another finishes a task",
    lines=[
        Line("Jordan", "Morning. So the user table migration is stuck. I'm waiting on the DBA to approve the schema change and it's been two days now."),
        Line("Sarah", "That's frustrating. Want me to ping them?"),
        Line("Jordan", "Yeah that would help. Other than that, I did finish setting up the staging environment. That's done."),
        Line("Sarah", "Great. I'm still on the OAuth flow, should be done by end of day."),
    ],
    expected_actions=[
        ExpectedAction(kind="FLAG_BLOCKER", card_id="CAD-5"),
        ExpectedAction(kind="MOVE_CARD", card_id="CAD-7", to_status="DONE"),
    ],
    voice_map={"Jordan": "Puck", "Sarah": "Kore"},
)
