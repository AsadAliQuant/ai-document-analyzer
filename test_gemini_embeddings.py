import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gemini_ocr import GEMINI_OCR_PIPELINE_VERSION
from gemini_gateway import GeminiCancelledError, GeminiGateway, GeminiRequestError
import large_doc_manager
from large_doc_manager import GeminiEmbeddingClient, LargeDocumentManager


class _FakeEmbedding:
    def __init__(self, values):
        self.values = values


class _FakeModels:
    def __init__(self):
        self.requests = []

    def embed_content(self, model, contents, config):
        self.requests.append((model, contents, config))
        return type(
            "Response",
            (),
            {
                "embeddings": [
                    _FakeEmbedding([float(index)] * GeminiEmbeddingClient.DIMENSION)
                    for index, _content in enumerate(contents)
                ]
            },
        )()


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()
        self.closed = False

    def close(self):
        self.closed = True


class _FakeTypes:
    HttpOptions = staticmethod(lambda **kwargs: type("HttpOptions", (), kwargs)())
    EmbedContentConfig = staticmethod(lambda **kwargs: type("EmbedContentConfig", (), kwargs)())
    class Part:
        @staticmethod
        def from_text(text):
            return type("PartValue", (), {"text": text})()
    class Content:
        def __init__(self, role, parts):
            self.role = role
            self.parts = parts


class _FakeSdk:
    def __init__(self, client):
        self.client = client
    def Client(self, **_kwargs):
        return self.client


class GeminiEmbeddingClientTests(unittest.TestCase):
    def _embedding_client(self):
        fake_client = _FakeClient()
        with patch.object(
            large_doc_manager,
            "GeminiGateway",
            lambda key: GeminiGateway(key, sdk=_FakeSdk(fake_client), types_module=_FakeTypes),
        ):
            client = GeminiEmbeddingClient("test-key")
        return client, fake_client

    def test_documents_are_sent_as_separate_content_objects(self):
        embedding_client, fake_client = self._embedding_client()

        vectors = embedding_client.embed_documents(
            ["first chunk", "second chunk"],
            title="example.pdf",
        )

        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), GeminiEmbeddingClient.DIMENSION)
        model, contents, config = fake_client.models.requests[0]
        self.assertEqual(model, "gemini-embedding-2")
        self.assertEqual(len(contents), 2)
        self.assertEqual(config.output_dimensionality, 768)
        self.assertEqual(contents[0].parts[0].text, "title: example.pdf | text: first chunk")

    def test_query_uses_question_answering_instruction(self):
        embedding_client, fake_client = self._embedding_client()

        vector = embedding_client.embed_query("What is the conclusion?")

        self.assertEqual(len(vector), GeminiEmbeddingClient.DIMENSION)
        _model, contents, _config = fake_client.models.requests[0]
        self.assertEqual(
            contents[0].parts[0].text,
            "task: question answering | query: What is the conclusion?",
        )

    def test_close_releases_sdk_client(self):
        embedding_client, fake_client = self._embedding_client()

        embedding_client.close()

        self.assertTrue(fake_client.closed)

    def test_rate_limit_error_is_user_friendly(self):
        error = GeminiEmbeddingClient._friendly_error(
            GeminiRequestError("quota", "Gemini usage limit reached.")
        )
        self.assertIn("free-tier limit", str(error))

    def test_cancellation_between_embedding_batches_stops_followup_requests(self):
        embedding_client, fake_client = self._embedding_client()
        with patch.object(
            GeminiGateway,
            "check_cancelled",
            side_effect=[None, None, GeminiCancelledError("cancelled")],
        ):
            with self.assertRaises(GeminiCancelledError):
                embedding_client.embed_documents(["chunk"] * 70)
        self.assertEqual(len(fake_client.models.requests), 1)

    def test_large_input_is_split_into_safe_batches(self):
        embedding_client, fake_client = self._embedding_client()
        texts = ["x" * 1200 for _index in range(70)]

        vectors = embedding_client.embed_documents(texts, title="large.txt")

        self.assertEqual(len(vectors), len(texts))
        self.assertGreater(len(fake_client.models.requests), 1)
        for _model, contents, _config in fake_client.models.requests:
            self.assertLessEqual(len(contents), GeminiEmbeddingClient.MAX_BATCH_ITEMS)


class _FakeEmbeddingClient:
    def embed_documents(self, texts, title="none"):
        return [
            [float(index + 1)] * GeminiEmbeddingClient.DIMENSION
            for index, _text in enumerate(texts)
        ]

    def embed_query(self, query):
        return [1.0] * GeminiEmbeddingClient.DIMENSION

    def close(self):
        pass


class DocumentKeyTests(unittest.TestCase):
    def test_image_key_is_stable_for_same_pipeline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "image.png"
            image_path.write_bytes(b"image")
            manager = LargeDocumentManager(temp_dir)

            first = manager.compute_document_key(
                str(image_path),
                processing_version=GEMINI_OCR_PIPELINE_VERSION,
            )
            second = manager.compute_document_key(
                str(image_path),
                processing_version=GEMINI_OCR_PIPELINE_VERSION,
            )

            self.assertEqual(first, second)

    def test_versioned_image_key_differs_from_old_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "image.jpg"
            image_path.write_bytes(b"image")
            manager = LargeDocumentManager(temp_dir)

            old_key = manager.compute_document_key(str(image_path))
            new_key = manager.compute_document_key(
                str(image_path),
                processing_version=GEMINI_OCR_PIPELINE_VERSION,
            )

            self.assertNotEqual(old_key, new_key)

    def test_different_pipeline_version_changes_image_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "image.jpeg"
            image_path.write_bytes(b"image")
            manager = LargeDocumentManager(temp_dir)

            first = manager.compute_document_key(str(image_path), processing_version="ocr:v1")
            second = manager.compute_document_key(str(image_path), processing_version="ocr:v2")

            self.assertNotEqual(first, second)

    def test_normal_document_keeps_legacy_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            document_path = Path(temp_dir) / "document.txt"
            document_path.write_text("text", encoding="utf-8")
            manager = LargeDocumentManager(temp_dir)
            stat = os.stat(document_path)
            payload = f"{os.path.abspath(document_path)}::{stat.st_size}::{int(stat.st_mtime)}"
            try:
                import hashlib
                expected = hashlib.md5(payload.encode("utf-8"), usedforsecurity=False).hexdigest()
            except TypeError:
                import hashlib
                expected = hashlib.md5(payload.encode("utf-8")).hexdigest()

            self.assertEqual(manager.compute_document_key(str(document_path)), expected)


class VectorStoreMetadataTests(unittest.TestCase):
    def test_old_embedding_store_is_invalidated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LargeDocumentManager(temp_dir)
            doc_key = "old-store"
            store_dir = Path(manager.doc_store_path(doc_key))
            (store_dir / "qdrant_db").mkdir(parents=True)
            (store_dir / "metadata.json").write_text(
                json.dumps({"embedding_model": "sentence-transformers/all-MiniLM-L6-v2"}),
                encoding="utf-8",
            )

            self.assertFalse(manager.has_vector_store(doc_key))

    def test_current_embedding_store_is_recognized(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LargeDocumentManager(temp_dir)
            doc_key = "current-store"
            store_dir = Path(manager.doc_store_path(doc_key))
            (store_dir / "qdrant_db").mkdir(parents=True)
            (store_dir / "metadata.json").write_text(
                json.dumps(
                    {
                        "embedding_model": manager.EMBEDDING_MODEL,
                        "embedding_dimension": manager.EMBEDDING_DIMENSION,
                        "embedding_format_version": manager.EMBEDDING_FORMAT_VERSION,
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(manager.has_vector_store(doc_key))

    def test_document_can_be_indexed_and_retrieved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LargeDocumentManager(temp_dir)
            manager._embedding = lambda api_key=None: _FakeEmbeddingClient()
            doc_key = "rag-store"

            chunk_count = manager.prepare_document(
                doc_key,
                "example.txt",
                "Alpha is the first topic.\n\nBeta is the second topic.",
                chunk_size=25,
                chunk_overlap=0,
            )
            documents = manager.retrieve_context(doc_key, "What is alpha?", k=chunk_count)

            self.assertGreaterEqual(chunk_count, 2)
            self.assertEqual(len(documents), chunk_count)
            self.assertTrue(any("Alpha" in document.page_content for document in documents))


if __name__ == "__main__":
    unittest.main()
