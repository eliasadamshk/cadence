from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="new_tickets",
    description="Team identifies new work that needs tracking",
    lines=[
        Line("Marcus", "One thing that came up yesterday, we need to add input validation to the signup form. Got a bug report about it."),
        Line("Sarah", "Yeah I saw that. We should also add CSRF protection to all the forms while we're at it."),
        Line("Marcus", "Good call. I can take the validation one. The CSRF thing is probably bigger though."),
        Line("Jordan", "I'll pick up CSRF once I'm unblocked on the migration."),
    ],
    expected_actions=[
        ExpectedAction(kind="CREATE_CARD", title_contains="input validation", assignee="Marcus", to_status="TODO"),
        ExpectedAction(kind="CREATE_CARD", title_contains="CSRF", to_status="TODO"),
    ],
    voice_map={"Marcus": "Charon", "Sarah": "Kore", "Jordan": "Puck"},
)
