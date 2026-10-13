# quizpublish

Open-source SDK: generate structured quizzes with any LLM, publish to form providers (Google Forms first; more later).

## Install

```bash
pip install -e .
```

## Quick start

```python
from quizpublish import OpenAIProvider, generate_quiz, GoogleFormsPublisher

llm = OpenAIProvider(model="gpt-4o-mini")  # or plug in your own LLMProvider
quiz = generate_quiz("Python", 5, "Multiple Choice", llm)

# credentials = google.oauth2.credentials.Credentials(...)
# result = GoogleFormsPublisher(credentials).publish("My Quiz", quiz, "Multiple Choice")
# print(result.responder_uri)
```

## Bring your own model

Implement `complete_json(system, user) -> dict` (see `LLMProvider`) and pass it to `generate_quiz`.

## Providers

| Provider | Class |
|----------|--------|
| Google Forms | `GoogleFormsPublisher` |
| Typeform | planned |
| Microsoft Forms | planned |

## License

MIT
