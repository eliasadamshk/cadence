from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="no_actions",
    description="Casual discussion with no actionable standup updates. Tests for false positives.",
    lines=[
        Line("Sarah", "Did anyone see the outage on AWS last night? Took down half the internet."),
        Line("Marcus", "Yeah I saw that. Glad we weren't affected."),
        Line("Jordan", "We should probably think about multi-region at some point. Not now though."),
        Line("Sarah", "Agreed. Maybe next quarter. Anyway, anything else for standup?"),
        Line("Marcus", "Nope, I think we're good."),
    ],
    expected_actions=[],
    voice_map={"Sarah": "Kore", "Marcus": "Charon", "Jordan": "Puck"},
)
