from evals.scenarios import ExpectedAction, Line, Scenario

scenario = Scenario(
    name="reassignment",
    description="Work gets reassigned between team members, card completed",
    lines=[
        Line("Marcus", "So I finished reviewing the staging environment setup. Looks good, Jordan."),
        Line("Jordan", "Thanks. I'm going to hand off the dashboard chart colors to Sarah since she's better with the design stuff."),
        Line("Sarah", "Sure, I'll take that. Also the email notification templates that Marcus did are already merged and deployed."),
        Line("Marcus", "Yep, that one's fully done. Deployed yesterday."),
    ],
    expected_actions=[
        ExpectedAction(kind="MOVE_CARD", card_id="CAD-7", to_status="DONE"),
        ExpectedAction(kind="UPDATE_CARD", card_id="CAD-3", assignee="Sarah"),
    ],
    voice_map={"Marcus": "Charon", "Jordan": "Puck", "Sarah": "Kore"},
)
