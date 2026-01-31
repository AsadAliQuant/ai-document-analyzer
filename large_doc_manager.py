import hashlib
import json
import os
import time
from typing import List, Optional, Any

try:
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.models import Distance, VectorParams  # type: ignore
    _qdrant_available = True
except Exception:
    QdrantClient = None  # type: ignore
    Distance = None  # type: ignore
    VectorParams = None  # type: ignore
    _qdrant_available = False

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document


class LargeDocumentManager:
    """Manage chunking and vector store persistence for large documents."""

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
        # Local cache directory for ML models (embeddings, OCR, etc.)
        self.models_dir = os.path.join(self.base_dir, "models")
        os.makedirs(self.models_dir, exist_ok=True)
        if not _qdrant_available:
            raise RuntimeError(
                "Qdrant is not available. Install 'qdrant-client' to enable vector storage."
            )

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    def compute_document_key(self, file_path: str) -> str:
        """Return a stable key representing the file path, size, and mtime."""
        abs_path = os.path.abspath(file_path)
        try:
            stat = os.stat(abs_path)
            payload = f"{abs_path}::{stat.st_size}::{int(stat.st_mtime)}"
        except OSError:
            payload = abs_path
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
    ) -> int:
        """Split text, embed, and persist to Qdrant. Returns chunk count."""
        print(f"prepare_document called for doc_key: {doc_key}, file: {file_path}")
        clean_text = (text or "").strip()
        print(f"Clean text length: {len(clean_text)}")
        if not clean_text:
            raise ValueError("Document contains no extractable text.")

        # Prepare directory
        store_dir = self.doc_store_path(doc_key)
        self._reset_directory(store_dir)
        os.makedirs(store_dir, exist_ok=True)

        # Persist raw extracted text for debugging/inspection
        self._write_raw_text(store_dir, clean_text)

        # Import text splitter lazily to avoid importing heavy deps at startup
        splitter = None
        splitter_import_error: Optional[BaseException] = None
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        except Exception as e1:
            splitter_import_error = e1
            try:
                from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            except Exception as e2:
                splitter_import_error = e2

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
        print(f"Created {len(raw_chunks)} raw chunks")
        documents: List[Document] = [
            Document(page_content=chunk, metadata={"source": file_path, "chunk_index": idx})
            for idx, chunk in enumerate(raw_chunks)
            if chunk.strip()
        ]
        print(f"Created {len(documents)} documents after filtering")
        if not documents:
            raise ValueError("Failed to create document chunks for vector store.")

        print("Creating embeddings")
        embeddings = self._embedding()
        print("Embeddings created successfully")

        # Create Qdrant vector store
        qdrant_dir = os.path.join(store_dir, "qdrant_db")
        
        # Aggressive cleanup with retries
        if os.path.exists(qdrant_dir):
            import shutil
            for attempt in range(3):
                try:
                    shutil.rmtree(qdrant_dir)
                    break
                except Exception as cleanup_err:
                    if attempt < 2:
                        print(f"Cleanup attempt {attempt + 1} failed, retrying...")
                        time.sleep(0.5)
                    else:
                        print(f"Warning: Could not remove old qdrant_dir: {cleanup_err}")
        
        client = None
        try:
            print("Creating Qdrant vector store")
            # Use QdrantClient directly to avoid langchain compatibility issues
            client = QdrantClient(path=qdrant_dir)
            collection_name = f"doc_{doc_key}"
            
            # Get embedding dimension from first document
            sample_embedding = embeddings.embed_query(documents[0].page_content[:100])
            embedding_dim = len(sample_embedding)
            
            # Create or recreate collection
            try:
                client.delete_collection(collection_name)
            except Exception:
                pass
            
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
            )
            
            # Add documents with embeddings
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            vectors = embeddings.embed_documents(texts)
            
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
            print("Qdrant vector store created successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to create Qdrant vector store: {e}"
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
        print(f"prepare_document completed, returning {len(documents)} chunks")
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

    def retrieve_context(self, doc_key: str, query: str, k: int = 25) -> List[Document]:
        store_dir = self.doc_store_path(doc_key)
        qdrant_dir = os.path.join(store_dir, "qdrant_db")
        
        if not os.path.isdir(qdrant_dir):
            return []
        
        qdrant_client = None
        try:
            embeddings = self._embedding()
            qdrant_client = QdrantClient(path=qdrant_dir)
            collection_name = f"doc_{doc_key}"
            
            # Embed the query
            query_vector = embeddings.embed_query(query)
            
            # Search using QdrantClient directly
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=max(1, int(k)),
            )
            
            # Convert results to Document objects
            results = []
            for hit in search_results:
                payload = hit.payload or {}
                page_content = payload.get("page_content", "")
                metadata = payload.get("metadata", {})
                results.append(Document(page_content=page_content, metadata=metadata))
            
            return results
        except Exception as e:
            print(f"Error retrieving context from Qdrant: {e}")
            return []
        finally:
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
    def _embedding(self) -> Any:
        print("Initializing HuggingFaceEmbeddings with all-MiniLM-L6-v2")
        model_kwargs = {}
        try:
            import torch  # type: ignore
            try:
                if torch.cuda.is_available():
                    model_kwargs = {"device": "cuda"}
            except Exception:
                pass
        except Exception:
            pass
        # Force cache to app-specific models dir so we can bundle/copy for offline use
        # Import HuggingFaceEmbeddings lazily to avoid importing transformers/torch at startup
        try:
            from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
        except Exception as e:
            raise RuntimeError("langchain-huggingface not available. Please install 'langchain-huggingface'.") from e

        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=self.models_dir,
            model_kwargs=model_kwargs,
        )


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
            "created_at": int(time.time()),
        }
        with open(os.path.join(store_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

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
