# Python Version Compatibility Guide

## Current Vector Store: Qdrant

The application now uses **Qdrant** as the vector database, which is compatible with Python Python 3.11. Qdrant runs embedded (in-process) and requires no external server.

## Migration Steps

### 1. Check Your Python Version

```powershell
python --version
# Only tested and works with 3.11
```

Qdrant is compatible with all modern Python versions. You do NOT need to downgrade or change your Python installation.

### 2. Install Python (if needed)

If you need to install Python:

1. **Download Python:**
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11+ (recommended: 3.11)
   - Choose "Windows installer (64-bit)"

2. **Install Python:**
   - Run the downloaded installer
   - **IMPORTANT:** Check "Add Python to PATH"
   - Choose "Customize installation"
   - Enable all optional features (pip, tcl/tk, documentation, etc.)
   - Click "Install"
   - Wait for installation to complete

3. **Verify Installation:**
   ```powershell
   python --version
   # Should output: Python 3.11.x or higher
   
   pip --version
   ```

### 3. Clean Your Virtual Environment (if upgrading)

If you're upgrading from an older installation, navigate to your project directory and remove the old virtual environment:

```powershell
cd "f:\Asad\Talha Projects\ai-document-analyzer"

# Remove old .venv folder
Remove-Item -Recurse -Force .venv
```

### 4. Create New Virtual Environment with Python 3.11

```powershell
# Create new virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\.venv\Scripts\Activate.ps1

# Verify Python version in venv
python --version
# Should show Python 3.11.x
```

### 5. Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt

# This will install:
# - Qdrant (embedded vector database)
# - PyQt6 (UI framework)
# - Sentence Transformers (embeddings)
# - PyTorch (with CUDA support if available)
# - LangChain (document processing)
# - And all other dependencies
```

### 6. Verify Installation

```powershell
# Test Qdrant import
python -c "from qdrant_client import QdrantClient; print('Qdrant OK')"

# Test sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers OK')"

# Test PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

# Check if CUDA is available (optional, for GPU acceleration)
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

### 7. Run Your Application

```powershell
# Make sure you're still in the activated virtual environment
python main.py
```

## Troubleshooting

### Issue: "Qdrant is not available"
**Solution:**
```powershell
pip install qdrant-client>=1.7.0
```

### Issue: "torch is not available" or CUDA errors
**Solution:**
```powershell
# For CPU-only (works on any system):
pip install torch torchvision torchaudio

# For CUDA GPU support (NVIDIA GPUs):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "Execution Policy" error when activating venv
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Multiple Python versions installed
**Solution:**
```powershell
# Use py launcher to specify Python 3.11:
py -3.11 -m venv .venv

# Or specify full path to Python 3.11:
"C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv
```

### Issue: Old vector stores from ChromaDB/FAISS
**Solution:**
The new Qdrant implementation will create new vector stores. Old stores are incompatible and will be ignored. To clean up:

```powershell
# Close the application first, then:
Remove-Item -Recurse -Force "$env:APPDATA\AI Document Analyzer\vector_store"
```

Re-process your documents after starting the app again.

## What Changed in the Code?

1. **Vector Store Backend:**
   - ❌ Removed: ChromaDB, FAISS
   - ✅ Added: Qdrant (embedded, in-process)

2. **Image Processing:**
   - ✅ Added: EasyOCR for local text extraction from images
   - ✅ Images now processed with OCR + RAG pipeline
   - ✅ GPU acceleration for OCR when CUDA available

3. **Embeddings:**
   - Fixed to use `sentence-transformers/all-MiniLM-L6-v2`
   - Automatic GPU/CPU detection via PyTorch

4. **Dependencies:**
   - Replaced `chromadb` with `qdrant-client>=1.7.0`
   - Includes `easyocr>=1.7.0` and `Pillow>=10.0.0` for OCR
   - Updated build configuration in `build_complete.bat`

5. **Files Modified:**
   - `large_doc_manager.py` - Updated for embedded Qdrant
   - `main_window.py` - OCR extraction and RAG for images
   - `requirements.txt` - Updated dependencies
   - `build_complete.bat` - Updated PyInstaller config
   - `LARGE_DOC_GUIDE.md` - Updated documentation

## Advantages of Qdrant + EasyOCR

- ✅ **No External Server:** Qdrant runs embedded in-process, no background service needed
- ✅ **Python Version Flexibility:** Works with Python 3.8 through 3.13+
- ✅ **Simple:** Pure Python implementation, no Rust compilation
- ✅ **Fast:** Efficient in-memory and persistent storage
- ✅ **Portable:** Easy to bundle with PyInstaller
- ✅ **GPU Support:** Automatic CUDA acceleration for embeddings AND OCR when available
- ✅ **OCR Privacy:** All text extraction happens locally, no cloud API calls
- ✅ **Offline:** Complete privacy, all data stays local
- ✅ **Image Support:** Full RAG pipeline for images via OCR

## Next Steps

After migration:
1. Test document processing with a sample PDF
2. **Test image OCR** with a sample image containing text
3. Verify Q&A functionality works for both documents and images
4. Check GPU acceleration status (if you have NVIDIA GPU)
5. Re-process any previously analyzed large documents/images

## Need Help?

If you encounter issues:
1. Check Python version: `python --version` (should be 3.11.x)
2. Verify venv is activated (you should see `(.venv)` in terminal prompt)
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
4. Check error messages in the application console
