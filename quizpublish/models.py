from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

QuestionType = Literal["Multiple Choice", "Checkboxes", "Dropdown", "Paragraph"]

CHOICE_TYPES = {"Multiple Choice", "Checkboxes", "Dropdown"}

GOOGLE_CHOICE_TYPE = {
    "Multiple Choice": "RADIO",
    "Checkboxes": "CHECKBOX",
    "Dropdown": "DROP_DOWN",
}


class QuizQuestion(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question cannot be empty")
        return value

    @field_validator("options")
    @classmethod
    def strip_options(cls, value: list[str]) -> list[str]:
        return [opt.strip() for opt in value if str(opt).strip()]


class QuizQuestionSet(BaseModel):
    questions: list[QuizQuestion] = Field(min_length=1)

    def as_form_pairs(
        self, question_type: QuestionType, num_questions: int | None = None
    ) -> list[tuple[str, str]]:
        """Convert to UI-friendly (question, options_text) pairs."""
        needs_options = question_type in CHOICE_TYPES
        pairs: list[tuple[str, str]] = []

        for item in self.questions:
            if needs_options:
                if len(item.options) < 2:
                    continue
                pairs.append((item.question, "\n".join(item.options[:4])))
            else:
                pairs.append((item.question, ""))

        if not pairs:
            raise ValueError("No valid questions after validation.")

        if num_questions is not None:
            return pairs[:num_questions]
        return pairs

    @classmethod
    def from_form_pairs(
        cls, pairs: list[tuple[str, str]], question_type: QuestionType
    ) -> QuizQuestionSet:
        """Build a quiz set from edited UI pairs."""
        needs_options = question_type in CHOICE_TYPES
        questions: list[QuizQuestion] = []

        for question, raw_options in pairs:
            q = question.strip()
            if not q:
                continue
            if needs_options:
                options = [
                    line.strip() for line in raw_options.split("\n") if line.strip()
                ]
                questions.append(QuizQuestion(question=q, options=options))
            else:
                questions.append(QuizQuestion(question=q, options=[]))

        return cls(questions=questions)
