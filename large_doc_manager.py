import hashlib
import json
import os
import time
from typing import List, Optional

try:
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.models import Distance, VectorParams  # type: ignore
    _qdrant_available = True
except Exception:
    QdrantClient = None  # type: ignore
    Distance = None  # type: ignore
    VectorParams = None  # type: ignore
    _qdrant_available = False

from langchain_core.documents import Document
from gemini_gateway import GeminiCancelledError, GeminiGateway


class GeminiEmbeddingClient:
    """Generate retrieval embeddings with Gemini Embedding 2."""

    MODEL = "gemini-embedding-2"
    DIMENSION = 768
    MAX_REQUEST_TOKENS = 24000
    MAX_BATCH_ITEMS = 32

    def __init__(self, api_key: str) -> None:
        key = (api_key or "").strip()
        if not key:
            raise RuntimeError(
                "A Gemini API key is required for document indexing and semantic search. "
                "Add it in Settings and try again."
            )
        self._gateway = GeminiGateway(key)

    def close(self) -> None:
        self._gateway.close()

    def embed_documents(self, texts: List[str], title: str = "none") -> List[List[float]]:
        clean_title = (title or "none").strip() or "none"
        prompts = [
            f"title: {clean_title} | text: {(text or '').strip()}"
            for text in texts
            if (text or "").strip()
        ]
        if not prompts:
            return []

        vectors: List[List[float]] = []
        for batch in self._build_batches(prompts):
            vectors.extend(self._embed_separate(batch))
        return vectors

    def embed_query(self, query: str) -> List[float]:
        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("The search question cannot be empty.")
        prompt = f"task: question answering | query: {clean_query}"
        return self._embed_separate([prompt])[0]

    def _build_batches(self, prompts: List[str]) -> List[List[str]]:
        batches: List[List[str]] = []
        current: List[str] = []
        estimated_tokens = 0

        for prompt in prompts:
            # Character-based estimation avoids an extra tokenizer dependency.
            prompt_tokens = max(1, (len(prompt) + 2) // 3)
            if prompt_tokens > self.MAX_REQUEST_TOKENS:
                raise RuntimeError(
                    "A document chunk is too large for Gemini Embedding. Reduce the configured chunk size."
                )
            if current and (
                len(current) >= self.MAX_BATCH_ITEMS
                or estimated_tokens + prompt_tokens > self.MAX_REQUEST_TOKENS
            ):
                batches.append(current)
                current = []
                estimated_tokens = 0
            current.append(prompt)
            estimated_tokens += prompt_tokens

        if current:
            batches.append(current)
        return batches

    def _embed_separate(self, prompts: List[str]) -> List[List[float]]:
        try:
            result = self._gateway.embed_contents(prompts, self.DIMENSION)
        except GeminiCancelledError:
            raise
        except Exception as exc:
            raise self._friendly_error(exc) from exc

        embeddings = getattr(result, "embeddings", None) or []
        vectors = [list(getattr(item, "values", None) or []) for item in embeddings]
        if len(vectors) != len(prompts) or any(len(vector) != self.DIMENSION for vector in vectors):
            raise RuntimeError("Gemini returned an invalid embedding response. Please try again.")
        return vectors

    @staticmethod
    def _friendly_error(exc: Exception) -> RuntimeError:
        category = getattr(exc, "category", "service")
        if category == "quota":
            return RuntimeError(
                "Gemini Embedding free-tier limit was reached. Wait for the quota to reset and try again."
            )
        if category == "auth":
            return RuntimeError(
                "Gemini rejected the API key. Check the Gemini API key in Settings."
            )
        if category in {"network", "timeout"}:
            return RuntimeError(
                "Gemini Embedding could not connect to the internet. Check the connection and try again."
            )
        return RuntimeError("Gemini Embedding request failed. Please try again shortly.")


class LargeDocumentManager:
    """Manage chunking and vector store persistence for large documents."""

    EMBEDDING_MODEL = GeminiEmbeddingClient.MODEL
    EMBEDDING_DIMENSION = GeminiEmbeddingClient.DIMENSION
    EMBEDDING_FORMAT_VERSION = 1

    def _fallback_split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        # Minimal dependency-free chunking fallback for packaged builds
        data = (text or "").strip()
        if not data:
            return []
        try:
            size = int(chunk_size)
        except Exception:
            size = 1200
        try:
            overlap = int(chunk_overlap)
        except Exception:
            overlap = 200

        if size <= 0:
            size = 1200
        if overlap < 0:
            overlap = 0
        if overlap >= size:
            overlap = max(0, size - 1)

        step = max(1, size - overlap)
        chunks: List[str] = []
        start = 0
        n = len(data)
        while start < n:
            end = min(n, start + size)
            chunk = data[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= n:
                break
            start += step
        return chunks

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.vector_base_dir = os.path.join(self.base_dir, "vector_store")
        os.makedirs(self.vector_base_dir, exist_ok=True)
        if not _qdrant_available:
            raise RuntimeError(
                "Qdrant is not available. Install 'qdrant-client' to enable vector storage."
            )

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    def compute_document_key(self, file_path: str, processing_version: Optional[str] = None) -> str:
        """Return a stable key for the file and optional processing pipeline."""
        abs_path = os.path.abspath(file_path)
        try:
            stat = os.stat(abs_path)
            payload = f"{abs_path}::{stat.st_size}::{int(stat.st_mtime)}"
        except OSError:
            payload = abs_path
        if processing_version:
            payload = f"{payload}::processing_version={processing_version}"
        try:
            return hashlib.md5(payload.encode("utf-8"), usedforsecurity=False).hexdigest()
        except TypeError:
            return hashlib.md5(payload.encode("utf-8")).hexdigest()

    def doc_store_path(self, doc_key: str) -> str:
        return os.path.join(self.vector_base_dir, doc_key)

    def chunks_path(self, doc_key: str) -> str:
        return os.path.join(self.doc_store_path(doc_key), "chunks.json")

    def metadata_path(self, doc_key: str) -> str:
        return os.path.join(self.doc_store_path(doc_key), "metadata.json")

    def backend_marker_path(self, doc_key: str) -> str:
        return os.path.join(self.doc_store_path(doc_key), "backend.json")

    def raw_text_path(self, doc_key: str) -> str:
        """Path to the raw extracted text file for a document."""
        return os.path.join(self.doc_store_path(doc_key), "raw_extracted.txt")

    def has_vector_store(self, doc_key: str) -> bool:
        store_dir = self.doc_store_path(doc_key)
        if not os.path.isdir(store_dir):
            return False

        metadata = self._read_metadata(doc_key)
        if (
            metadata.get("embedding_model") != self.EMBEDDING_MODEL
            or metadata.get("embedding_dimension") != self.EMBEDDING_DIMENSION
            or metadata.get("embedding_format_version") != self.EMBEDDING_FORMAT_VERSION
        ):
            return False

        # Check for Qdrant artifacts
        qdrant_dir = os.path.join(store_dir, "qdrant_db")
        if os.path.isdir(qdrant_dir):
            return True
        # Check backend marker
        marker = self.backend_marker_path(doc_key)
        if os.path.exists(marker):
            try:
                with open(marker, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("backend") == "qdrant"
            except Exception:
                pass
        return False

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------
    def prepare_document(
        self,
        doc_key: str,
        file_path: str,
        text: str,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        api_key: Optional[str] = None,
    ) -> int:
        """Split text, embed, and persist to Qdrant. Returns chunk count."""
        clean_text = (text or "").strip()
        if not clean_text:
            raise ValueError("Document contains no extractable text.")

        store_dir = self.doc_store_path(doc_key)

        # Import text splitter lazily to avoid importing heavy deps at startup
        splitter = None
        splitter_import_error: Optional[BaseException] = None
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        except Exception as exc:
            splitter_import_error = exc

        if splitter is not None:
            raw_chunks = splitter.split_text(clean_text)
        else:
            if splitter_import_error is not None:
                print(f"Text splitter import failed, using fallback chunker: {splitter_import_error}")
            raw_chunks = self._fallback_split_text(clean_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            if not raw_chunks and splitter_import_error is not None:
                raise RuntimeError(
                    f"Text splitter unavailable and fallback chunker produced no chunks. "
                    f"Splitter import error: {splitter_import_error}"
                ) from splitter_import_error
        documents: List[Document] = [
            Document(page_content=chunk, metadata={"source": file_path, "chunk_index": idx})
            for idx, chunk in enumerate(raw_chunks)
            if chunk.strip()
        ]
        if not documents:
            raise ValueError("Failed to create document chunks for vector store.")

        embeddings = self._embedding(api_key)

        # Generate vectors before replacing an existing store. If Gemini is
        # unavailable, the last valid index remains usable.
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        document_title = os.path.basename(file_path) if file_path else "none"
        try:
            vectors = embeddings.embed_documents(texts, title=document_title)
        finally:
            embeddings.close()
        if len(vectors) != len(texts):
            raise RuntimeError("Gemini did not return an embedding for every document chunk.")

        # Replace the local Qdrant store only after embedding succeeds.
        self._reset_directory(store_dir)
        os.makedirs(store_dir, exist_ok=True)
        self._write_raw_text(store_dir, clean_text)
        qdrant_dir = os.path.join(store_dir, "qdrant_db")

        client = None
        try:
            # Use QdrantClient directly to avoid langchain compatibility issues
            client = QdrantClient(path=qdrant_dir)
            collection_name = f"doc_{doc_key}"
            
            # Create or recreate collection
            try:
                client.delete_collection(collection_name)
            except Exception:
                pass

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.EMBEDDING_DIMENSION, distance=Distance.COSINE),
            )

            # Upload points
            from qdrant_client.models import PointStruct
            points = [
                PointStruct(
                    id=idx,
                    vector=vector,
                    payload={"page_content": text, "metadata": metadata}
                )
                for idx, (vector, text, metadata) in enumerate(zip(vectors, texts, metadatas))
            ]
            client.upsert(collection_name=collection_name, points=points)
            
            used_backend = "qdrant"
        except Exception as e:
            message = str(e)
            if "Gemini" in message or "API key" in message or "Google Gen AI SDK" in message:
                raise RuntimeError(message) from e
            raise RuntimeError(
                f"Failed to create Qdrant vector store: {message}"
            ) from e
        finally:
            # Close the client to release locks
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
            # Small delay to ensure Windows releases file locks
            time.sleep(0.2)

        self._write_backend_marker(store_dir, backend=used_backend)

        self._write_chunks(store_dir, documents)
        self._write_metadata(
            store_dir,
            file_path=file_path,
            chunk_count=len(documents),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return len(documents)

    def _write_raw_text(self, store_dir: str, content: str) -> None:
        path = os.path.join(store_dir, "raw_extracted.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
        except Exception as e:
            print(f"Warning: Failed to write raw text dump: {e}")

    # ------------------------------------------------------------------
    # Retrieval & context
    # ------------------------------------------------------------------
    def build_summary_context(self, doc_key: str, max_chars: int = 8000) -> str:
        chunks = self._read_chunks(doc_key)
        if not chunks:
            return ""
        collected: List[str] = []
        total = 0
        for entry in chunks:
            content = (entry.get("content") or "").strip()
            if not content:
                continue
            collected.append(content)
            total += len(content)
            if total >= max_chars:
                break
        return "\n\n".join(collected)

    def retrieve_context(
        self,
        doc_key: str,
        query: str,
        k: int = 25,
        api_key: Optional[str] = None,
    ) -> List[Document]:
        if not self.has_vector_store(doc_key):
            return []
        store_dir = self.doc_store_path(doc_key)
        qdrant_dir = os.path.join(store_dir, "qdrant_db")
        
        if not os.path.isdir(qdrant_dir):
            return []
        
        qdrant_client = None
        embeddings = None
        try:
            embeddings = self._embedding(api_key)
            qdrant_client = QdrantClient(path=qdrant_dir)
            collection_name = f"doc_{doc_key}"
            
            # Embed the query
            query_vector = embeddings.embed_query(query)
            
            # Search using QdrantClient directly
            query_response = qdrant_client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=max(1, int(k)),
                with_payload=True,
            )

            # Convert results to Document objects
            results = []
            for hit in query_response.points:
                payload = hit.payload or {}
                page_content = payload.get("page_content", "")
                metadata = payload.get("metadata", {})
                results.append(Document(page_content=page_content, metadata=metadata))
            
            return results
        except GeminiCancelledError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve document context: {e}") from e
        finally:
            if embeddings is not None:
                embeddings.close()
            if qdrant_client is not None and hasattr(qdrant_client, "close"):
                try:
                    qdrant_client.close()
                except Exception:
                    pass

    def read_full_text(self, doc_key: str) -> str:
        """Return the full original text for a processed document.

        Prefers the raw extracted text dump; falls back to concatenating chunks
        if the raw file is missing.
        """
        try:
            path = self.raw_text_path(doc_key)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        except Exception:
            pass
        # Fallback: join chunk contents
        try:
            chunks = self._read_chunks(doc_key)
            if not chunks:
                return ""
            parts: List[str] = []
            for entry in chunks:
                content = (entry.get("content") or "").strip()
                if content:
                    parts.append(content)
            return "\n\n".join(parts)
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _embedding(self, api_key: Optional[str] = None) -> GeminiEmbeddingClient:
        api_key = (api_key or "").strip()
        if not api_key:
            raise RuntimeError(
                "A Gemini API key is required for document indexing and semantic search. "
                "Add it in Settings and try again."
            )

        return GeminiEmbeddingClient(api_key)


    def _write_backend_marker(self, store_dir: str, backend: str) -> None:
        try:
            with open(os.path.join(store_dir, "backend.json"), "w", encoding="utf-8") as f:
                json.dump({"backend": backend}, f)
        except Exception:
            pass

    def _read_backend_marker(self, doc_key: str) -> str:
        try:
            with open(self.backend_marker_path(doc_key), "r", encoding="utf-8") as f:
                data = json.load(f)
            return str(data.get("backend", ""))
        except Exception:
            return ""

    def _reset_directory(self, path: str) -> None:
        if not os.path.isdir(path):
            return
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except OSError:
                    pass
        try:
            os.rmdir(path)
        except OSError:
            pass

    def _write_chunks(self, store_dir: str, documents: List[Document]) -> None:
        payload = [
            {
                "index": int(doc.metadata.get("chunk_index", idx)),
                "content": doc.page_content,
            }
            for idx, doc in enumerate(documents)
        ]
        payload.sort(key=lambda item: item.get("index", 0))
        path = os.path.join(store_dir, "chunks.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _write_metadata(
        self,
        store_dir: str,
        file_path: str,
        chunk_count: int,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        metadata = {
            "file_path": file_path,
            "chunk_count": chunk_count,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "embedding_model": self.EMBEDDING_MODEL,
            "embedding_dimension": self.EMBEDDING_DIMENSION,
            "embedding_format_version": self.EMBEDDING_FORMAT_VERSION,
            "created_at": int(time.time()),
        }
        with open(os.path.join(store_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _read_metadata(self, doc_key: str) -> dict:
        path = self.metadata_path(doc_key)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def _read_chunks(self, doc_key: str) -> List[dict]:
        path = self.chunks_path(doc_key)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []
