from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="mixed",
    description="Realistic standup with a mix of moves, creates, blockers, and chatter",
    lines=[
        Line("Sarah", "Alright let's do this. I finished the OAuth login yesterday and pushed it to review."),
        Line("Marcus", "I'll review that this morning. My payment webhook fix got approved so I'm merging that now. Done."),
        Line("Jordan", "Nice. I'm still blocked on the migration, same as yesterday. DBA hasn't responded."),
        Line("Sarah", "Okay. Today I'm picking up the rate limiting middleware."),
        Line("Marcus", "Oh before I forget, we got a request from the product team to add dark mode support. We should track that."),
        Line("Jordan", "Yeah let's add that to the backlog. Once I'm unblocked I'll finish the migration and then maybe grab the onboarding tooltip tour."),
    ],
    expected_actions=[
        ExpectedAction(kind="MOVE_CARD", card_id="CAD-1", to_status="IN_REVIEW"),
        ExpectedAction(kind="MOVE_CARD", card_id="CAD-2", to_status="DONE"),
        ExpectedAction(kind="FLAG_BLOCKER", card_id="CAD-5"),
        ExpectedAction(kind="UPDATE_CARD", card_id="CAD-4", assignee="Sarah"),
        ExpectedAction(kind="CREATE_CARD", title_contains="dark mode", to_status="TODO"),
    ],
    voice_map={"Sarah": "Kore", "Marcus": "Charon", "Jordan": "Puck"},
)
