import json
import tempfile
import unittest
from pathlib import Path

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


class GeminiEmbeddingClientTests(unittest.TestCase):
    def test_documents_are_sent_as_separate_content_objects(self):
        embedding_client = GeminiEmbeddingClient("test-key")
        embedding_client._client = _FakeClient()

        vectors = embedding_client.embed_documents(
            ["first chunk", "second chunk"],
            title="example.pdf",
        )

        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), GeminiEmbeddingClient.DIMENSION)
        model, contents, config = embedding_client._client.models.requests[0]
        self.assertEqual(model, "gemini-embedding-2")
        self.assertEqual(len(contents), 2)
        self.assertEqual(config.output_dimensionality, 768)
        self.assertEqual(contents[0].parts[0].text, "title: example.pdf | text: first chunk")

    def test_query_uses_question_answering_instruction(self):
        embedding_client = GeminiEmbeddingClient("test-key")
        embedding_client._client = _FakeClient()

        vector = embedding_client.embed_query("What is the conclusion?")

        self.assertEqual(len(vector), GeminiEmbeddingClient.DIMENSION)
        _model, contents, _config = embedding_client._client.models.requests[0]
        self.assertEqual(
            contents[0].parts[0].text,
            "task: question answering | query: What is the conclusion?",
        )

    def test_rate_limit_error_is_user_friendly(self):
        error = GeminiEmbeddingClient._friendly_error(Exception("429 RESOURCE_EXHAUSTED"))
        self.assertIn("free-tier limit", str(error))

    def test_large_input_is_split_into_safe_batches(self):
        embedding_client = GeminiEmbeddingClient("test-key")
        embedding_client._client = _FakeClient()
        texts = ["x" * 1200 for _index in range(70)]

        vectors = embedding_client.embed_documents(texts, title="large.txt")

        self.assertEqual(len(vectors), len(texts))
        self.assertGreater(len(embedding_client._client.models.requests), 1)
        for _model, contents, _config in embedding_client._client.models.requests:
            self.assertLessEqual(len(contents), GeminiEmbeddingClient.MAX_BATCH_ITEMS)


class _FakeEmbeddingClient:
    def embed_documents(self, texts, title="none"):
        return [
            [float(index + 1)] * GeminiEmbeddingClient.DIMENSION
            for index, _text in enumerate(texts)
        ]

    def embed_query(self, query):
        return [1.0] * GeminiEmbeddingClient.DIMENSION


class VectorStoreMetadataTests(unittest.TestCase):
    def test_old_embedding_store_is_invalidated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LargeDocumentManager(temp_dir, api_key_provider=lambda: "test-key")
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
            manager = LargeDocumentManager(temp_dir, api_key_provider=lambda: "test-key")
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
            manager = LargeDocumentManager(temp_dir, api_key_provider=lambda: "test-key")
            manager._embedding = lambda: _FakeEmbeddingClient()
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
