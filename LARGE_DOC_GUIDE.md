# Document, Image OCR, and RAG Processing Guide

## Supported inputs

- PDF: text is extracted with PyPDF2. Scanned-PDF OCR is not supported.
- DOCX: text is extracted with python-docx.
- TXT: text is read directly.
- PNG/JPG/JPEG: the complete image is sent to Gemini for transcription.
- Pasted text: text is processed directly.

## Processing pipeline

```text
Document text or Gemini image transcription
    → 1200-character chunks with 200-character overlap
    → Gemini Embedding 2
    → embedded Qdrant store on the user's computer
    → bounded summary context or semantic retrieval
    → Gemini summary/Q&A
```

Image OCR is separate from summarization. Gemini first returns transcription only. The application saves that raw text, chunks and embeds it, and stores it in local Qdrant before summary or Q&A processing.

Summaries use a bounded context built from indexed chunks. Semantic questions send the question to Gemini Embedding 2, retrieve relevant passages from local Qdrant, and send those passages with the question and applicable conversation history to Gemini generation. For exact-count questions, Gemini classifies the intent and the application performs the actual count locally against the complete stored text.

OCR, intent classification, summaries, and Q&A use this ordered generation fallback:

1. `gemini-2.5-flash-lite`
2. `gemini-3.1-flash-lite`
3. `gemini-3.5-flash-lite`

The application advances only when a model is unavailable, not found, overloaded, or returns an appropriate server failure. Authentication, quota, timeout, validation, and other client failures are reported without trying another model.

## Requirements and privacy

A Gemini API key configured in Settings, an internet connection, and available API quota are required for supported AI processing.

The application sends the following data to Google Gemini:

- Complete PNG/JPG/JPEG image bytes for transcription.
- Extracted text chunks for Gemini Embedding 2 indexing.
- Selected document context for summaries.
- Questions for intent classification and query embedding.
- Retrieved passages, the current question, and applicable conversation history for semantic Q&A.

Source files are read locally. Extracted text, chunks, vectors, embedding metadata, and cached indexes remain in local Qdrant under `%APPDATA%/AI Document Analyzer/vector_store/`. Exact-count execution also happens locally after Gemini classifies the question. This local persistence does not provide offline AI inference.

OCR supports English, Arabic, and mixed-language images and preserves reading order and reasonable table/paragraph layout where possible. The OCR request treats text visible in an image as content to transcribe, not instructions to follow; it does not ask Gemini to summarize, translate, explain, or infer missing text.

Gemini quota or billing rules may apply.

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

Image cache keys include the Gemini OCR pipeline version. Therefore:

- An old EasyOCR-generated image index is not reused.
- An unchanged Gemini-processed image reuses its existing index and does not upload the image again.
- Modifying an image or changing the OCR pipeline version creates a new index.
- PDF, DOCX, TXT, and pasted-text keys are not invalidated by OCR changes.

Upgraded installations may retain old EasyOCR weights or indexes. The current application neither loads nor recreates local OCR/model weights. Obsolete weights may be removed manually if disk space is needed:

```text
%APPDATA%/AI Document Analyzer/models/easyocr/
```

## Q&A behavior

Semantic questions use Gemini Embedding 2 to search local Qdrant and Gemini generation to answer from retrieved document passages and applicable conversation history. Exact-count questions are first classified by Gemini, then counted deterministically against the complete locally stored transcription or extracted text rather than only retrieved chunks.

## Common errors

- **Missing key:** add the Gemini API key in Settings.
- **Invalid or unauthorized key:** verify the key and project permissions in Google AI Studio, then update Settings.
- **Quota/rate limit:** wait for quota reset or check billing/quota configuration.
- **Network failure or timeout:** check internet access and retry; all AI workflows depend on Gemini.
- **Generation models unavailable:** confirm access to at least one configured Flash-Lite model.
- **Embedding/indexing failure:** verify Gemini Embedding 2 access, the key, and the network, then reprocess the document.
- **Qdrant initialization/storage failure:** verify that the AppData directory is writable and has sufficient free space.
- **Unsupported, password-protected, or damaged document:** use a supported readable file.
- **Unsupported/damaged image:** use a readable PNG, JPG, or JPEG.
- **No readable image text:** use a clearer image containing visible text.
- **Safety block:** retry with different source content.

## Dependencies

Runtime document processing uses:

- `google-genai` for Gemini OCR, intent classification, summaries, Q&A, and embeddings
- `qdrant-client` for local vector and document-text persistence
- LangChain text splitters, with a dependency-free chunking fallback
- PyPDF2 and python-docx for document extraction
- Pillow for image handling

Ollama and local inference models are not supported. EasyOCR, sentence-transformers, Transformers, Torch, torchvision, OpenCV, scikit-image, SciPy, and scikit-learn are not part of the active document/OCR pipeline or supported package build.
