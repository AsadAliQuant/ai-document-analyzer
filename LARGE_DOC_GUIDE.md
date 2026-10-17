# Document, Image OCR, and RAG Processing Guide

## Supported inputs

- PDF: text is extracted with PyPDF2. Scanned-PDF OCR is not supported.
- DOCX: text is extracted with python-docx.
- TXT: text is read directly.
- PNG/JPG/JPEG: the full image is sent to Gemini 2.5 Flash-Lite for transcription, with Gemini 3.1 Flash-Lite and then Gemini 3.5 Flash-Lite as ordered fallbacks when the current model is unavailable.
- Pasted text: text is indexed directly.

## Processing pipeline

```text
Document text or Gemini image transcription
    → 1200-character chunks with 200-character overlap
    → Gemini Embedding 2
    → embedded Qdrant store on the user's computer
    → summary, semantic Q&A, and exact counting
```

Image OCR is intentionally separate from summarization. Gemini first returns transcription only. That raw text is then saved, chunked, embedded, and passed to the selected Gemini or Ollama summary model.

## Image OCR requirements and privacy

- A Gemini API key configured in Settings is required.
- An internet connection is required.
- The complete uploaded image is sent to Google Gemini for OCR.
- Gemini API quota and billing rules may apply.
- Selecting Ollama keeps final summary/Q&A generation local, but new image OCR and Gemini Embedding 2 indexing still use Google APIs.
- OCR supports English, Arabic, and mixed-language images.
- Images containing tables or multiple paragraphs preserve reading order and layout where reasonably possible.

The OCR request treats text visible in an image as content to transcribe, not as instructions to follow. It does not ask Gemini to summarize, translate, explain, or infer missing text.

## Caching

Document indexes live under:

```text
%APPDATA%/AI Document Analyzer/vector_store/
```

Each index stores:

- Qdrant vectors
- Ordered text chunks
- The complete raw extracted text used by exact counting
- Embedding metadata

Image cache keys include the Gemini OCR pipeline version. This means:

- An old EasyOCR-generated image index is not reused.
- An unchanged Gemini-processed image reuses its existing index and does not upload the image again.
- Modifying an image or changing the OCR pipeline version creates a new index.
- PDF, DOCX, TXT, and pasted-text keys are not invalidated by OCR changes.

Old EasyOCR weights and old image indexes are not deleted automatically. They can be removed manually if disk space is needed:

```text
%APPDATA%/AI Document Analyzer/models/easyocr/
```

## Q&A behavior

Semantic questions use Gemini Embedding 2 to retrieve relevant chunks from local Qdrant. Exact counting reads the complete raw transcription or extracted text rather than only retrieved chunks. Both Gemini and Ollama use the same indexed document content.

## Common errors

- Missing key: add the Gemini API key in Settings.
- Invalid key: verify the key in Google AI Studio and update Settings.
- Quota/rate limit: wait for quota reset or check billing/quota configuration.
- Network timeout: check the internet connection and retry.
- Models unavailable: confirm the account can access at least one configured Flash-Lite model (Gemini 2.5, 3.1, or 3.5).
- Unsupported/damaged image: use a readable PNG, JPG, or JPEG.
- No readable text: use a clearer image containing visible text.
- Safety block: retry with a different image.

## Dependencies

Runtime document processing uses:

- google-genai for Gemini OCR, summaries, Q&A, and embeddings
- qdrant-client for local vector storage
- langchain text splitters, with a dependency-free chunking fallback
- PyPDF2 and python-docx for document extraction
- ollama for optional local final-generation models

EasyOCR, Torch, torchvision, OpenCV, scikit-image, SciPy, and scikit-learn are not part of the active OCR pipeline or supported package build.
