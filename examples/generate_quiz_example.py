"""Example: generate a quiz with the open-source SDK (no Google publish)."""

from open_assessment_kit import OpenAIProvider, generate_quiz


def main() -> None:
    llm = OpenAIProvider()
    quiz = generate_quiz("Python", 3, "Multiple Choice", llm)
    for i, q in enumerate(quiz.questions, start=1):
        print(f"Q{i}. {q.question}")
        for opt in q.options:
            print(f"  - {opt}")
        print()


if __name__ == "__main__":
    main()
