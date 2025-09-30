# Large Document Processing Guide

## Overview
The AI Document Analyzer now supports processing large documents (PDFs, DOCX, TXT files with more than 2 pages) using advanced chunking and vector database technology. This enables efficient analysis and Q&A for documents that would otherwise be too large to process effectively.

## How It Works

### Automatic Detection
- Documents are automatically detected as "large" if they contain more than 2 pages (for PDFs) or equivalent content
- The system prompts users before proceeding with chunking

### Chunking Process
- Large documents are split into manageable chunks (1200 characters each with 200 character overlap)
- Each chunk is embedded using the configured Ollama model
- Chunks are stored in a local ChromaDB vector database

### RAG (Retrieval-Augmented Generation)
- For Q&A, relevant chunks are retrieved based on semantic similarity to the user's question
- The AI generates answers using the most relevant document passages
- Supports both Ollama and Gemini models

## User Experience

### First-Time Processing
1. Upload a large document (PDF/DOCX/TXT with >2 pages)
2. System detects large document and prompts for processing
3. Click "Yes" to proceed with chunking
4. Wait for chunking to complete (shows progress)
5. Summary generation begins using chunked content

### Subsequent Usage
- Previously processed documents load instantly from vector store
- No need to re-process the same document
- Q&A uses vector retrieval for accurate responses

## Technical Details

### Dependencies
- **LangChain**: Text splitting and vector store management
- **ChromaDB**: Embedded vector database
- **Ollama embeddings**: Any Ollama model can be used for embeddings

### Embedding Models
You can use any Ollama model for embeddings, not just `nomic-embed-text`. To use a different model:

1. **Pull your preferred model:**
   ```bash
   ollama pull llama3.2          # General purpose model
   ollama pull mistral           # Another option
   ollama pull llama3.1:8b       # Smaller/faster option
   ```

2. **Configure in Settings:**
   - Open Settings in the application
   - Enter your preferred model name in "Embedding Model" field
   - Click Save

3. **Supported Models:**
   - `nomic-embed-text` (recommended - optimized for embeddings)
   - `llama3.2`, `llama3.1:8b`, `mistral` (general purpose models)
   - Any other Ollama model

**Note:** While you can use general models like llama3 or mistral, specialized embedding models like `nomic-embed-text` typically provide better semantic similarity for document retrieval.

### Chunking Parameters
- **Chunk size**: 1200 characters
- **Overlap**: 200 characters
- **Embedding model**: Configurable via Settings

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

### Changing Embedding Model
1. Open Settings (gear icon in top-right)
2. Find "Embedding Model" field
3. Enter your preferred Ollama model name
4. Click Save
5. Restart the application for changes to take effect

### Default Model
- The default is `nomic-embed-text` which is optimized for embeddings
- For better performance, use specialized embedding models
- General purpose models work but may have lower retrieval accuracy

## Troubleshooting

### Common Issues

**"Model not found"**
- Ensure the model is pulled: `ollama pull <model-name>`
- Check model name spelling in Settings

**"Failed to process large document"**
- Check document is not corrupted or password-protected
- Ensure sufficient disk space for vector store

**Slow initial processing**
- First-time chunking can take time for large documents
- Subsequent loads are instant

**Poor Q&A quality**
- Try using `nomic-embed-text` instead of general models
- Specialized embedding models provide better semantic matching

### Manual Cleanup
To remove stored vector data:
1. Close the application
2. Delete the `vector_store` folder in `%APPDATA%/AI Document Analyzer/`
3. Restart the application

## Compatibility
- Works with all supported file formats: PDF, DOCX, TXT
- Compatible with both Ollama and Gemini backends
- Maintains backward compatibility with small documents
