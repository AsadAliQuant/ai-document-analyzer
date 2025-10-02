# Large Document & Image OCR Processing Guide

## Overview
The AI Document Analyzer supports processing large documents (PDFs, DOCX, TXT files with more than 2 pages) and **images with OCR** using advanced chunking and vector database technology. This enables efficient analysis and Q&A for documents and images that would otherwise be too large to process effectively.

## How It Works

### Automatic Detection
- **Documents**: Automatically detected as "large" if they contain more than 2 pages (for PDFs) or equivalent content
- **Images**: All uploaded images (PNG, JPG, JPEG) are processed with OCR
- The system prompts users before proceeding with processing

### Processing Pipeline
1. **OCR Extraction (Images)**:
   - Uses EasyOCR to extract text from images
   - Supports English and Arabic languages
   - GPU acceleration when CUDA is available (falls back to CPU)
   - Extracted text is treated like document text

2. **Chunking & Embedding**:
   - Documents/OCR text split into manageable chunks (1200 characters each with 200 character overlap)
   - Each chunk is embedded using sentence-transformers (all-MiniLM-L6-v2 model)
   - Chunks are stored in an embedded Qdrant vector database (runs in-process, no server needed)
   - GPU acceleration is used automatically when CUDA is available

### RAG (Retrieval-Augmented Generation)
- For Q&A, relevant chunks are retrieved based on semantic similarity to the user's question
- The AI generates answers using the most relevant document passages
- Supports both Ollama and Gemini models

## User Experience

### First-Time Processing

**For Documents:**
1. Upload a large document (PDF/DOCX/TXT with >2 pages)
2. System detects large document and prompts for processing
3. Click "Yes" to proceed with chunking
4. Wait for chunking to complete
5. Summary generation begins using chunked content

**For Images:**
1. Upload an image (PNG/JPG/JPEG)
2. System prompts for OCR processing
3. Click "Yes" to proceed with OCR extraction
4. EasyOCR extracts text from image (GPU-accelerated if available)
5. Extracted text is chunked and stored in vector database
6. Summary generated from OCR text using selected AI model
7. Q&A enabled for asking questions about image content

### Subsequent Usage
- Previously processed documents/images load instantly from vector store
- No need to re-process the same file
- Q&A uses vector retrieval for accurate responses
- Images are treated exactly like text documents after OCR

## Technical Details

### Dependencies
- **LangChain**: Text splitting and vector store management
- **Qdrant**: Embedded vector database (runs in-process, no server required)
- **Sentence Transformers**: all-MiniLM-L6-v2 for embeddings
- **PyTorch**: Enables GPU acceleration when CUDA is available
- **EasyOCR**: Local OCR engine for text extraction from images
- **Pillow (PIL)**: Image processing library

### OCR Engine
The application uses `EasyOCR` for text extraction:
- **Languages**: English and Arabic support built-in
- **GPU Acceleration**: Automatically uses CUDA GPU when available, falls back to CPU
- **Offline**: Downloads language models once (~100MB per language)
- **Accurate**: Deep learning-based recognition
- **Privacy**: All OCR processing happens locally

### Embedding Model
The application uses `sentence-transformers/all-MiniLM-L6-v2` for generating embeddings:
- **Optimized**: Specifically designed for semantic similarity
- **Fast**: Lightweight model (~90MB) with quick inference
- **GPU Support**: Automatically uses CUDA GPU when available, falls back to CPU
- **Offline**: Model downloads once and works completely offline
- **Reliable**: No dependency on external services

### Chunking Parameters
- **Chunk size**: 1200 characters
- **Overlap**: 200 characters
- **Embedding model**: sentence-transformers/all-MiniLM-L6-v2 (fixed)

### Storage Location
- Vector stores are saved in `%APPDATA%/AI Document Analyzer/vector_store/`
- Each document gets a unique key based on file path, size, and modification time
- Persistent storage ensures fast reloading

## Benefits

### Performance
- Handles documents of any size without memory issues
- Fast Q&A responses using vector similarity search
- Efficient storage with automatic deduplication

### Privacy
- All processing done locally
- No document content sent to external services
- Complete offline capability

### Accuracy
- Context-aware Q&A using relevant document chunks
- Better summarization for large documents
- Maintains document structure and meaning

## Configuration

### GPU Acceleration
The application automatically detects and uses NVIDIA CUDA GPUs when available:
- **Automatic Detection**: No configuration needed
- **CPU Fallback**: Works seamlessly on systems without GPU
- **Performance Boost**: Significantly faster embedding generation with GPU
- **Requirements**: CUDA-compatible GPU with appropriate PyTorch installation

## Troubleshooting

### Common Issues

**"Qdrant is not available"**
- Run: `pip install qdrant-client>=1.7.0`
- Reinstall dependencies from requirements.txt
- Works with any Python version (3.8+)

**"EasyOCR not installed"**
- Run: `pip install easyocr>=1.7.0 Pillow>=10.0.0`
- First run will download OCR models (~100MB per language)
- Ensure sufficient disk space

**"Failed to process image/document"**
- Check file is not corrupted or password-protected
- Ensure sufficient disk space for vector store
- Verify Qdrant and EasyOCR installed correctly
- For images: ensure image contains readable text

**"No text detected in the image"**
- Image may be blank or contain only graphics
- Try higher quality/resolution image
- Ensure text is clearly visible and not handwritten
- Check image is not corrupted

**Slow OCR processing**
- First-time processing downloads OCR models (one-time)
- CPU-only OCR can be slow for large/complex images
- GPU acceleration significantly speeds up OCR
- Install CUDA-enabled PyTorch for GPU support

**Slow initial processing**
- First-time chunking can take time for large documents
- Subsequent loads are instant
- Consider using CUDA GPU for faster embeddings and OCR

**Poor Q&A quality**
- Ensure document/image was processed successfully
- Try asking more specific questions
- Check that vector store was created properly
- For images: verify OCR extracted text correctly

### Manual Cleanup
To remove stored vector data:
1. Close the application
2. Delete the `vector_store` folder in `%APPDATA%/AI Document Analyzer/`
3. Restart the application

## Compatibility
- **Supported Formats**: PDF, DOCX, TXT, PNG, JPG, JPEG
- **Images**: All image formats processed with OCR + RAG pipeline
- **AI Backends**: Compatible with both Ollama (offline) and Gemini (online)
- **GPU Support**: Automatic CUDA acceleration for both OCR and embeddings
- **Languages**: English and Arabic OCR support
- Maintains backward compatibility with existing documents
