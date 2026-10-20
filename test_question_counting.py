import json
import unittest
from unittest.mock import patch

import main_window
from main_window import MainWindow


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

        with patch.object(main_window, "genai", object()), patch.object(
            window,
            "_generate_gemini_text",
            return_value=response,
        ) as generate:
            intent = window._classify_question_intent(
                "How many times does the word BASELINEQUARTZ appear in the document?",
                "gemini",
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


if __name__ == "__main__":
    unittest.main()
