from __future__ import annotations

from pydantic import ValidationError

from open_assessment_kit.llm.base import LLMProvider
from open_assessment_kit.models import CHOICE_TYPES, QuestionType, QuizQuestionSet


def build_generation_prompt(
    topic: str, num_questions: int, question_type: QuestionType
) -> str:
    if question_type in CHOICE_TYPES:
        if question_type == "Checkboxes":
            style = (
                "checkbox-style questions where more than one option can be correct. "
                "Write questions that naturally allow selecting multiple answers."
            )
        elif question_type == "Dropdown":
            style = "single-answer dropdown questions with clear, concise options."
        else:
            style = "single-answer multiple-choice questions."

        return f"""
You are an AI teacher. Generate {num_questions} {style} about "{topic}".

Return ONLY valid JSON with this exact shape:
{{
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"]
    }}
  ]
}}

Rules:
- Exactly {num_questions} items in "questions"
- Each item must have exactly 4 non-empty options
- No markdown, no extra keys, no explanations
"""

    return f"""
You are an AI teacher. Generate {num_questions} open-ended paragraph questions about "{topic}".
They should require a written explanation, not a one-word answer.

Return ONLY valid JSON with this exact shape:
{{
  "questions": [
    {{
      "question": "Question text?",
      "options": []
    }}
  ]
}}

Rules:
- Exactly {num_questions} items in "questions"
- "options" must be an empty array for paragraph questions
- No markdown, no extra keys, no explanations
"""


def generate_quiz(
    topic: str,
    num_questions: int,
    question_type: QuestionType,
    llm: LLMProvider,
) -> QuizQuestionSet:
    """
    Generate a structured quiz using any LLMProvider.

    Example:
        from open_assessment_kit import OpenAIProvider, generate_quiz
        quiz = generate_quiz("Python", 5, "Multiple Choice", OpenAIProvider())
    """
    prompt = build_generation_prompt(topic, num_questions, question_type)
    try:
        data = llm.complete_json(
            system="You return only valid JSON that matches the user's schema.",
            user=prompt,
        )
        quiz = QuizQuestionSet.model_validate(data)
    except (ValidationError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid structured quiz output: {e}") from e

    # Trim / filter via the same rules used by the UI helpers
    pairs = quiz.as_form_pairs(question_type, num_questions)
    return QuizQuestionSet.from_form_pairs(pairs, question_type)
