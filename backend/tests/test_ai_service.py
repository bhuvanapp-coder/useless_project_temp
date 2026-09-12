import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.ai_service import (
    SYSTEM_PROMPT,
    generate_actual_topic_refusal,
    generate_panic_mode,
    generate_useless_lesson,
    generate_useless_questions,
)


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="Page 17 is the academic event of the century.")


class StructuredFakeResponses(FakeResponses):
    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text='{"title":"Page 17: The Sequel","explanation":"Page 17 is important because it is page 17.","key_points":["It exists"],"fake_importance":"100/100","memory_trick":"Remember 17 forever.","exam_relevance":"Guaranteed to be mentioned by someone."}'
        )


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


class AiServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = {
            "document_id": "doc-ai",
            "title": "Margins and Other Emergencies",
            "author": "Professor Footer",
            "page_count": 17,
            "pages": [{"page_number": 17, "detected_page_number": 17, "font_sizes": [12, 18]}],
            "structure": {"repeated_headers": [{"text": "COURSE NOTES", "page_numbers": [1, 17]}]},
        }
        self.client = FakeClient()

    def test_all_generators_use_shared_personality_and_document_context(self) -> None:
        generators = [
            lambda: generate_useless_lesson(self.document, "Teach me Unit 3", client=self.client),
            lambda: generate_useless_questions(self.document, client=self.client),
            lambda: generate_panic_mode(self.document, client=self.client),
            lambda: generate_actual_topic_refusal(self.document, "photosynthesis", client=self.client),
        ]

        for generate in generators:
            result = generate()
            if isinstance(result, dict) and "questions" in result:
                self.assertEqual(result["title"], "🔥 MOST IMPORTANT EXAM QUESTIONS")
            elif isinstance(result, dict) and "steps" in result:
                self.assertEqual(result["title"], "🚨 EXAM PANIC MODE")
            elif isinstance(result, dict):
                self.assertEqual(result["title"], "A Very Important Page")
            else:
                self.assertEqual(result, "Page 17 is the academic event of the century.")

        self.assertEqual(len(self.client.responses.calls), 4)
        for call in self.client.responses.calls:
            self.assertIn("world's least useful academic assistant", call["instructions"])
            self.assertIn("Margins and Other Emergencies", call["input"])
            self.assertIn("page_number\": 17", call["input"])
            self.assertEqual(call["model"], "gpt-4o-mini")

    def test_actual_topic_refusal_mentions_requested_topic_in_prompt(self) -> None:
        generate_actual_topic_refusal(self.document, "quantum mechanics", client=self.client)
        self.assertIn("quantum mechanics", self.client.responses.calls[0]["input"])
        self.assertIn("Refuse to explain", self.client.responses.calls[0]["input"])

    def test_lesson_parses_structured_json_for_frontend(self) -> None:
        structured_client = FakeClient()
        structured_client.responses = StructuredFakeResponses()
        result = generate_useless_lesson(self.document, client=structured_client)
        self.assertEqual(result["title"], "Page 17: The Sequel")
        self.assertEqual(result["key_points"], ["It exists"])
        self.assertEqual(result["fake_importance"], "100/100")

    def test_panic_plan_uses_selected_duration(self) -> None:
        result = generate_panic_mode(self.document, "10 minutes", client=self.client)
        self.assertEqual(result["duration"], "10 minutes")
        self.assertEqual(result["total_seconds"], 600)
        self.assertGreater(len(result["steps"]), 0)
        self.assertIn("fictional comedy plan", result["disclaimer"])

    def test_missing_key_is_reported_without_constructing_client(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            result = generate_useless_lesson(self.document)
            self.assertEqual(result["mode"], "local_fallback")
            self.assertIn("Page 17", result["title"])

    def test_quiz_panic_and_refusal_work_without_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            quiz = generate_useless_questions(self.document)
            panic = generate_panic_mode(self.document, "10 minutes")
            refusal = generate_actual_topic_refusal(self.document, "calculus")

        self.assertEqual(quiz["mode"], "local_fallback")
        self.assertGreater(len(quiz["questions"]), 0)
        self.assertEqual(panic["total_seconds"], 600)
        self.assertIn("Error 404", refusal)


if __name__ == "__main__":
    unittest.main()
