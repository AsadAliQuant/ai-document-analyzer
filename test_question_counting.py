import json
import unittest
from unittest.mock import patch

import main_window
from main_window import MainWindow, _QAWorker


class _Signal:
    def __init__(self):
        self.calls = []

    def emit(self, *args):
        self.calls.append(args)


class _StoredDocumentManager:
    def __init__(self, text):
        self.text = text

    def has_vector_store(self, _doc_key):
        return True

    def read_full_text(self, _doc_key):
        return self.text


class QuestionCountingTests(unittest.TestCase):
    def _window(self, text=""):
        window = MainWindow.__new__(MainWindow)
        window._current_lang = "en"
        window._qa_document_text = text
        window.large_doc_manager = _StoredDocumentManager(text)
        return window

    def test_gemini_structured_intent_is_requested_and_parsed(self):
        window = self._window()
        response = json.dumps({
            "operation": "literal_occurrence_count",
            "target": "BASELINEQUARTZ",
            "unit": "",
        })

        with patch.object(
            window,
            "_generate_gemini_text",
            return_value=response,
        ) as generate:
            intent = window._classify_question_intent(
                "How many times does the word BASELINEQUARTZ appear in the document?",
                "ignored",
                "key",
            )

        self.assertEqual(intent["operation"], "literal_occurrence_count")
        self.assertEqual(intent["target"], "BASELINEQUARTZ")
        schema = generate.call_args.kwargs["response_json_schema"]
        self.assertEqual(schema["properties"]["operation"]["type"], "string")

    def test_baselinequartz_is_counted_as_literal_target(self):
        text = "BASELINEQUARTZ " * 7 + "\nother line"
        result = self._window(text)._handle_counting_intent({
            "operation": "literal_occurrence_count",
            "target": "BASELINEQUARTZ",
            "unit": "",
        }, "doc")

        self.assertEqual(
            result,
            'The word/phrase "BASELINEQUARTZ" appears 7 times in the document.',
        )

    def test_structural_line_count_still_works(self):
        text = "one\n\ntwo\nthree"
        result = self._window(text)._handle_counting_intent({
            "operation": "structural_count",
            "target": "",
            "unit": "lines",
        }, "doc")

        self.assertEqual(result, "Number of lines in the document: 3")

    def test_invalid_intent_falls_back_to_semantic_qa(self):
        intent = self._window()._parse_question_intent(
            '{"operation":"structural_count","target":"","unit":"pipeline"}'
        )

        self.assertEqual(
            intent,
            {"operation": "semantic_qa", "target": "", "unit": ""},
        )

    def test_arabic_literal_count_uses_localized_response(self):
        window = self._window("علامة علامة علامة")
        window._current_lang = "ar"

        result = window._handle_counting_intent({
            "operation": "literal_occurrence_count",
            "target": "علامة",
            "unit": "",
        })

        self.assertIn("علامة", result)
        self.assertIn("3", result)
        self.assertNotIn("appears", result)

    def test_counting_question_bypasses_semantic_qa(self):
        class Window:
            def _classify_question_intent(self, _question, _model, _key):
                return {
                    "operation": "literal_occurrence_count",
                    "target": "TOKEN",
                    "unit": "",
                }

            def _handle_counting_intent(self, _intent, _doc_key):
                return 'The word/phrase "TOKEN" appears 4 times in the document.'

            def answer_question_gemini(self, *_args):
                raise AssertionError("semantic Q&A must not run for a count operation")

        worker = _QAWorker(Window(), {
            "model": "ignored-model",
            "messages": [{"role": "user", "content": "How many TOKEN values?"}],
            "summary": "summary",
            "input_text": "TOKEN TOKEN TOKEN TOKEN",
            "gemini_key": "captured-key",
            "doc_key": "doc-key",
        }, 11)
        worker.finished = _Signal()
        worker.error = _Signal()

        worker.run()

        self.assertEqual(
            worker.finished.calls,
            [('The word/phrase "TOKEN" appears 4 times in the document.', 11)],
        )
        self.assertEqual(worker.error.calls, [])


if __name__ == "__main__":
    unittest.main()
