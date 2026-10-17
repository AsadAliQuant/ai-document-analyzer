# AI Document Analyzer - Online-Only Architecture Design

Based on my comprehensive codebase exploration, I'll now design a lightweight, online-only architecture for your AI Document Analyzer.

## Architecture Analysis Complete

### Current Architecture Problems Identified

**Startup Bottlenecks (60-120s):**
- Offline Bootstrap - Downloads/validates sentence-transformers (400+ MB) and EasyOCR models (100+ MB)
- Heavy ML Dependencies - torch, transformers, sentence-transformers load at startup
- Qdrant Vector Store - Local database initialization with embedded models
- Admin Rights - Required for file locks, model caching in system directories

**Dependency Weight Analysis:**
- torch: ~800MB (CPU-only build)
- transformers + sentence-transformers: ~500MB
- Qdrant client + vector storage: ~100MB
- EasyOCR + dependencies: ~200MB
- LangChain suite: ~50MB
- Ollama client: Minimal, but requires Ollama server

---

## 1. DEPENDENCY TRANSFORMATION

### Remove Completely (Offline/Local ML)
- ollama>=0.1.9 (~5MB + requires Ollama server)
- sentence-transformers>=2.2.0 (~200MB)
- torch>=2.0.0 (~800MB - largest culprit)
- langchain-huggingface>=0.0.1 (~50MB)
- scipy==1.11.4 (~100MB)
- scikit-learn>=1.3.0 (~50MB)
- qdrant-client>=1.7.0 (~50MB)
- langchain-qdrant>=0.1.0 (~10MB)
- easyocr>=1.7.0 (~150MB)

### Keep Core (UI & Framework)
- PyQt6>=6.6 (~50MB - Required)

### Document Processing
- PyPDF2>=3.0.1 (~1MB - Keep)
- python-docx>=1.0.1 (~1MB - Keep)
- Pillow>=10.0.0 (~10MB - Keep)

### Online AI
- google-generativeai>=0.7.2 (~5MB - PRIMARY AI ENGINE)

### Auth & Security
- cryptography>=41.0.0 (~5MB - Keep)
- keyring>=24.0.0 (~1MB - Keep)
- portalocker>=2.0.0 (~1MB - Keep)

### LangChain - MINIMAL SUBSET
- langchain-core>=0.2.0 (~10MB - Keep)
- langchain-text-splitters>=0.2.0 (~2MB - Keep)

### Add New (Cloud Services)
- google-cloud-vision>=3.4.0 (~5MB - Replace EasyOCR)
- *OR use Gemini vision directly (already have google-generativeai)*
- requests>=2.31.0 (Already included)

**Estimated Size Reduction:** 2.2GB → ~90MB (96% reduction)

---

## 2. ARCHITECTURE CHANGES

### A. Remove Local Vector Store (Qdrant)
**Current Flow:**
Document → Extract Text → Chunk → Embed (Local) → Store (Qdrant) → Retrieve → Answer

**New Flow (Option 1 - Simpler, No RAG):**
Document → Extract Text → Chunk → Send Full Context to Gemini → Answer

**New Flow (Option 2 - Cloud RAG):**
Document → Extract Text → Chunk → Gemini Embedding API → In-Memory Search → Answer

*Recommendation: Option 1 for Phase 1*
- Gemini 2.5 Flash supports 1M token context window.
- Average document fits entirely in context.
- No need for vector search.
- Simplest implementation, fastest startup.

### B. Replace EasyOCR with Cloud OCR
*Recommendation: Use Gemini Vision (already integrated)*

```python
# Example for Gemini Vision
import google.generativeai as genai

def extract_text_from_image_gemini(image_path: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    response = model.generate_content([
        "Extract all text from this image. Return only the extracted text, preserving layout and structure.",
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    return response.text
```

### C. Simplify Document Processing Pipeline
Remove `offline_bootstrap.py`, `large_doc_manager.py` (Qdrant/vector logic). Replace with `online_doc_processor.py`.

### D. Update Startup Sequence
Remove offline model prep, Qdrant init, Ollama checks, embedding model loading.
**Estimated Startup:** 3-5 seconds (95% reduction).

---

## 3. FILE STORAGE STRATEGY (No Admin Rights)
Use `%APPDATA%` (user-specific, no admin needed):
- `C:\Users\<user>\AppData\Roaming\AI Document Analyzer\`
- `config.json` (keys, settings)
- `doc_cache\` (tmp cache)
- `logs\` (app logs)

---

## 4. Q&A PROCESSING CHANGES
**New Flow:** Question → Load cached chunks → Smart chunk selection → Send to Gemini.

---

## 5. AUTHENTICATION (Keep As-Is)
Works well, no changes needed.

---

## 6. WINDOWS INSTALLER STRATEGY
*Recommendation: Start with Option A (PyInstaller + Inno Setup)*
1. PyInstaller onedir (faster startup, smaller size).
2. Wrap in Inno Setup installer.

---

## 7. IMPLEMENTATION PLAN

### Phase 1: Core Migration (Week 1)
- Create `online_doc_processor.py` (replace `large_doc_manager.py`)
- Replace EasyOCR with Gemini Vision
- Remove Ollama references
- Update `startup_helper.py`

### Phase 2: Cleanup (Week 1)
- Remove unused dependencies from `requirements.txt`
- Delete `offline_bootstrap.py`
- Update PyInstaller spec

### Phase 3: Installer (Week 2)
- Create Inno Setup script
- Test installation without admin

### Phase 4: Optimization (Week 2)
- Add progress indicators
- Implement request caching
- Add offline mode detection

---

## CRITICAL FILES FOR IMPLEMENTATION
- `requirements.txt`
- `large_doc_manager.py`
- `main_window.py`
- `startup_helper.py`
- `AI Document Analyzer.spec`

---

## APPENDIX: DETAILED COMPARISONS

| Feature | Before | After | Tradeoff |
| :--- | :--- | :--- | :--- |
| Offline Mode | Full | None | Requires internet (acceptable) |
| OCR Quality | Good | Better | Gemini Vision handles complex layouts |
| Doc Size Limit | Unlimited | ~1M tokens (~500 pages) | Rarely exceeded |
| Startup Speed | 60-120s | 3-5s | 95% faster |
| Install Size | 2-3GB | 150MB | 95% smaller |
| Admin Rights | Required | Not required | Much better UX |
| Cost | Free (local) | ~$0.001-0.01/doc | Negligible |

*Recommendation: Skip RAG for Phase 1, add later if needed*
