from app.schemas.coding import AIFeedbackResponse


def test_ai_feedback_accepts_extended_coding_feedback_fields():
    feedback = AIFeedbackResponse(
        correctness="Correct",
        explanation="Your approach is valid and handles the edge cases.",
        time_complexity="O(n)",
        space_complexity="O(1)",
        optimization_suggestions=["Use a two-pointer strategy."],
        edge_cases_missed=["Empty input"],
    )

    assert feedback.correctness == "Correct"
    assert feedback.explanation == "Your approach is valid and handles the edge cases."
    assert feedback.time_complexity == "O(n)"
    assert feedback.space_complexity == "O(1)"
    assert feedback.optimization_suggestions == ["Use a two-pointer strategy."]
    assert feedback.edge_cases_missed == ["Empty input"]
