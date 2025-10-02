import hashlib
import json
import os
import time
from typing import List, Optional

try:
    import torch  # type: ignore
except Exception:
    torch = None  # type: ignore

try:
    from qdrant_client import QdrantClient  # type: ignore
    from langchain_community.vectorstores import Qdrant  # type: ignore
    _qdrant_available = True
except Exception:
    QdrantClient = None  # type: ignore
    Qdrant = None  # type: ignore
    _qdrant_available = False

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


class LargeDocumentManager:
    """Manage chunking and vector store persistence for large documents."""

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

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        raw_chunks = splitter.split_text(clean_text)
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
        
        vector_store = None
        try:
            print("Creating Qdrant vector store")
            # Let Qdrant.from_documents create the client internally
            vector_store = Qdrant.from_documents(
                documents=documents,
                embedding=embeddings,
                path=qdrant_dir,
                collection_name=f"doc_{doc_key}",
                force_recreate=True,
            )
            used_backend = "qdrant"
            print("Qdrant vector store created successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to create Qdrant vector store: {e}"
            ) from e
        finally:
            # Close the client to release locks
            if vector_store is not None:
                client = getattr(vector_store, "client", None) or getattr(vector_store, "_client", None)
                if client is not None and hasattr(client, "close"):
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

    def retrieve_context(self, doc_key: str, query: str, k: int = 15) -> List[Document]:
        store_dir = self.doc_store_path(doc_key)
        qdrant_dir = os.path.join(store_dir, "qdrant_db")
        
        if not os.path.isdir(qdrant_dir):
            return []
        
        qdrant_client = None
        try:
            embeddings = self._embedding()
            qdrant_client = QdrantClient(path=qdrant_dir)

            vector_store = Qdrant(
                client=qdrant_client,
                collection_name=f"doc_{doc_key}",
                embeddings=embeddings,
            )
            results = vector_store.similarity_search(query, k=max(1, int(k)))
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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _embedding(self) -> HuggingFaceEmbeddings:
        print("Initializing HuggingFaceEmbeddings with all-MiniLM-L6-v2")
        model_kwargs = {}
        try:
            if torch is not None and torch.cuda.is_available():
                model_kwargs = {"device": "cuda"}
        except Exception:
            pass
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs=model_kwargs)


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
