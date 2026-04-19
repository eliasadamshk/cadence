from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="simple_updates",
    description="Basic status updates: one card to review, one card picked up",
    lines=[
        Line("Sarah", "Hey everyone. So yesterday I wrapped up the OAuth login flow. It's ready for review now."),
        Line("Marcus", "Nice. I'll take a look at that. My payment webhook fix is still in review, no updates there."),
        Line("Sarah", "Cool. Today I'm going to pick up the API rate limiting ticket since it's unassigned."),
        Line("Marcus", "Sounds good. No blockers from my side."),
    ],
    expected_actions=[
        ExpectedAction(kind="MOVE_CARD", card_id="CAD-1", to_status="IN_REVIEW"),
        ExpectedAction(kind="UPDATE_CARD", card_id="CAD-4", assignee="Sarah"),
    ],
    voice_map={"Sarah": "Kore", "Marcus": "Charon"},
)
