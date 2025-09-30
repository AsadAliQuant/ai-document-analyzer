import hashlib
import json
import os
import time
from typing import List, Optional
import numpy as np

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
try:
    from langchain_community.vectorstores import FAISS  # type: ignore
    _faiss_available = True
except Exception:
    FAISS = None  # type: ignore
    _faiss_available = False


class LargeDocumentManager:
    """Manage chunking and vector store persistence for large documents."""

    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        self.vector_base_dir = os.path.join(self.base_dir, "vector_store")
        os.makedirs(self.vector_base_dir, exist_ok=True)
        # No external DB settings required for FAISS

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

    def simple_index_path(self, doc_key: str) -> str:
        return os.path.join(self.doc_store_path(doc_key), "simple_index.npz")

    def has_vector_store(self, doc_key: str) -> bool:
        store_dir = self.doc_store_path(doc_key)
        if not os.path.isdir(store_dir):
            return False
        # FAISS artifacts
        faiss_idx = os.path.join(store_dir, "index.faiss")
        faiss_pkl = os.path.join(store_dir, "index.pkl")
        if os.path.exists(faiss_idx) and os.path.exists(faiss_pkl):
            return True
        if os.path.exists(self.simple_index_path(doc_key)):
            return True
        # Check backend marker
        marker = self.backend_marker_path(doc_key)
        if os.path.exists(marker):
            try:
                with open(marker, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return bool(data.get("backend"))
            except Exception:
                return False
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
        """Split text, embed, and persist to Chroma. Returns chunk count."""
        print(f"prepare_document called for doc_key: {doc_key}, file: {file_path}")
        clean_text = (text or "").strip()
        print(f"Clean text length: {len(clean_text)}")
        if not clean_text:
            raise ValueError("Document contains no extractable text.")

        # Prepare directory
        store_dir = self.doc_store_path(doc_key)
        self._reset_directory(store_dir)
        os.makedirs(store_dir, exist_ok=True)

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

        used_backend = ""
        if _faiss_available:
            try:
                print("Creating FAISS vector store")
                vector_store = FAISS.from_documents(documents, embeddings)
                vector_store.save_local(store_dir)
                used_backend = "faiss"
                print("FAISS vector store created")
            except Exception as e:
                print(f"Error creating FAISS vector store: {e}")
        if not used_backend:
            print("Falling back to simple NumPy-based index...")
            self._build_simple_index(store_dir, documents, embeddings)
            used_backend = "simple"
            print("Simple index created successfully")

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

    def retrieve_context(self, doc_key: str, query: str, k: int = 4) -> List[Document]:
        # Try Chroma path first if available
        store = self._load_vector_store(doc_key)
        if store is not None:
            try:
                return store.similarity_search(query, k=k)
            except Exception:
                pass
        # Fallback: simple index retrieval
        idx_path = self.simple_index_path(doc_key)
        if not os.path.exists(idx_path):
            return []
        try:
            data = np.load(idx_path)
            vectors = data["vectors"]  # shape (n, d), normalized
            indices = data["indices"].astype(int)
            # Embed query and normalize
            q = self._embedding().embed_query(query)
            qv = np.array(q, dtype=np.float32)
            qn = qv / (np.linalg.norm(qv) + 1e-12)
            sims = vectors @ qn
            topk = np.argsort(-sims)[: max(1, int(k))]
            # Build Documents using chunks.json
            chunks = self._read_chunks(doc_key)
            out: List[Document] = []
            for pos in topk:
                chunk_idx = int(indices[int(pos)])
                # Find content by index
                try:
                    entry = next((c for c in chunks if int(c.get("index", -1)) == chunk_idx), None)
                    content = (entry or {}).get("content", "")
                except Exception:
                    content = ""
                if content:
                    out.append(Document(page_content=content, metadata={"chunk_index": chunk_idx}))
            return out
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _embedding(self) -> HuggingFaceEmbeddings:
        print("Initializing HuggingFaceEmbeddings with all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def _load_vector_store(self, doc_key: str):
        store_dir = self.doc_store_path(doc_key)
        if not os.path.isdir(store_dir):
            return None
        # Prefer backend marker to decide how to load
        backend = self._read_backend_marker(doc_key)
        if backend == "faiss" and _faiss_available:
            try:
                # In langchain 0.2+, allow_dangerous_deserialization may be needed
                return FAISS.load_local(store_dir, self._embedding(), allow_dangerous_deserialization=True)
            except Exception:
                return None
        # Fallback: simple index
        if os.path.exists(self.simple_index_path(doc_key)):
            return None  # simple index will be used directly in retrieve_context
        return None

    def _build_simple_index(self, store_dir: str, documents: List[Document], embeddings: HuggingFaceEmbeddings) -> None:
        texts = [doc.page_content for doc in documents]
        idxs = [int(doc.metadata.get("chunk_index", i)) for i, doc in enumerate(documents)]
        # Compute embeddings
        vecs = embeddings.embed_documents(texts)
        # Normalize for cosine similarity
        arr = np.array(vecs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        arr = arr / norms
        path = os.path.join(store_dir, "simple_index.npz")
        np.savez(path, vectors=arr, indices=np.array(idxs, dtype=np.int32))
        self._write_backend_marker(store_dir, backend="simple")

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
