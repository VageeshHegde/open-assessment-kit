from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from quizpublish.models import (
    CHOICE_TYPES,
    GOOGLE_CHOICE_TYPE,
    QuestionType,
    QuizQuestionSet,
)
from quizpublish.publishers.base import PublishResult


class GoogleFormsPublisher:
    """Publish a QuizQuestionSet to Google Forms using user OAuth credentials."""

    SCOPES = ("https://www.googleapis.com/auth/forms.body",)

    def __init__(self, credentials: Any) -> None:
        self._credentials = credentials
        self._service = build(
            "forms",
            "v1",
            credentials=credentials,
            discoveryServiceUrl=(
                "https://forms.googleapis.com/$discovery/rest?version=v1"
            ),
        )

    def publish(
        self,
        title: str,
        quiz: QuizQuestionSet,
        question_type: QuestionType,
        *,
        shuffle: bool = False,
    ) -> PublishResult:
        created = (
            self._service.forms()
            .create(body={"info": {"title": title}})
            .execute()
        )
        form_id = created["formId"]

        requests = []
        for idx, item in enumerate(quiz.questions):
            requests.append(
                self._build_item_request(item.question, item.options, question_type, shuffle, idx)
            )

        if requests:
            self._service.forms().batchUpdate(
                formId=form_id, body={"requests": requests}
            ).execute()

        responder_uri = created.get(
            "responderUri",
            f"https://docs.google.com/forms/d/{form_id}/viewform",
        )
        return PublishResult(
            provider="google",
            form_id=form_id,
            responder_uri=responder_uri,
            edit_uri=f"https://docs.google.com/forms/d/{form_id}/edit",
            question_count=len(requests),
        )

    def _build_item_request(
        self,
        question: str,
        options: list[str],
        question_type: QuestionType,
        shuffle: bool,
        index: int,
    ) -> dict[str, Any]:
        base_question: dict[str, Any] = {"required": True}

        if question_type in CHOICE_TYPES:
            base_question["choiceQuestion"] = {
                "type": GOOGLE_CHOICE_TYPE[question_type],
                "options": [{"value": opt} for opt in options],
                "shuffle": shuffle if question_type != "Dropdown" else False,
            }
        else:
            base_question["textQuestion"] = {"paragraph": True}

        return {
            "createItem": {
                "item": {
                    "title": question,
                    "questionItem": {"question": base_question},
                },
                "location": {"index": index},
            }
        }
