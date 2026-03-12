# AI Document Analyzer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

> A powerful PyQt6-based desktop application for AI-powered document and image analysis with intelligent chunking, OCR, and hybrid AI support (offline + cloud).

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Features in Detail](#features-in-detail)
  - [Large Document & Image Processing](#large-document--image-processing)
  - [Remote Lock System](#remote-lock-system)
  - [Vector Database & Persistence](#vector-database--persistence)
- [Building for Distribution](#building-for-distribution)
- [Server-PHP-Auth Backend](#server-php-auth-backend)
- [AI Models & Prompts](#ai-models--prompts)
- [Multi-Language Support](#multi-language-support)
- [Security & Privacy](#security--privacy)
- [GPU Acceleration](#gpu-acceleration)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)
- [Support](#support)

---

## Overview

**AI Document Analyzer** is a cross-platform Python desktop application that brings the power of artificial intelligence to document and image analysis. It seamlessly combines offline privacy with cloud-based capabilities, allowing users to choose their preferred AI backend.

### Key Value Propositions

- 🔒 **Complete Privacy**: Run entirely offline with Ollama—no data leaves your machine
- ☁️ **Flexible AI**: Switch between offline (Ollama/LLaMA) and cloud (Google Gemini) models
- 📄 **Smart Processing**: Automatically handles large documents with intelligent chunking and RAG
- 🖼️ **Image Intelligence**: Extract and analyze text from images with deep learning OCR
- 🌍 **Multilingual**: Full English/Arabic support for UI and OCR
- 🔐 **Enterprise-Ready**: Optional JWT-based authentication backend for centralized control
- 🎯 **Fast & Efficient**: GPU-accelerated embeddings and OCR when CUDA is available

---

## Key Features

### Document & Image Processing
- ✅ **Format Support**: PDF, DOCX, TXT, PNG, JPG, JPEG
- ✅ **Intelligent OCR**: EasyOCR with CUDA GPU acceleration
- ✅ **Large Document Handling**: Auto-detect 2+ page documents and process with RAG
- ✅ **Smart Chunking**: 1200-character chunks with 200-character overlap for optimal context
- ✅ **Vector Embeddings**: All-MiniLM-L6-v2 model for semantic search

### AI Capabilities
- ✅ **Document Summarization**: Structured JSON output with key points, methods, conclusions
- ✅ **Q&A Chat**: Ask questions about documents using Retrieval-Augmented Generation (RAG)
- ✅ **Image Analysis**: Extract text and analyze images with OCR + RAG pipeline
- ✅ **Dual AI Backends**: Offline (Ollama) or cloud-based (Google Gemini)

### User Experience
- ✅ **Multi-language UI**: Full English and Arabic interface support
- ✅ **PDF Export**: Export summaries and analysis as PDFs
- ✅ **System Tray Integration**: Minimize to system tray, quick access
- ✅ **Settings Dashboard**: Configure API keys, AI models, preferences
- ✅ **Persistent Vector Store**: Instant reloading of previously analyzed documents

### Advanced Features
- ✅ **Remote Lock System**: Disable the app remotely via Google Sheets
- ✅ **Offline Mode**: Works completely offline with Ollama backend
- ✅ **GPU Acceleration**: Automatic CUDA support for embeddings and OCR
- ✅ **Enterprise Auth**: Optional JWT-based authentication backend

---

## Technology Stack

### Frontend & UI
- **PyQt6** 6.6+ — Cross-platform desktop UI framework
- **Python** 3.8+ (3.11+ recommended) — Application runtime
- **QSS Stylesheets** — Modern application theming

### AI/ML Components
| Component | Library | Purpose |
|-----------|---------|---------|
| **Embeddings** | Sentence Transformers | Semantic vector embeddings |
| **OCR** | EasyOCR | Local text extraction from images |
| **Text Splitting** | LangChain | Intelligent document chunking |
| **Vector Store** | Qdrant | Embedded vector database (in-process) |
| **Deep Learning** | PyTorch | Model inference with CUDA support |

### AI Inference Engines
- **Ollama** — Local LLaMA models for offline inference
- **Google Generative AI** — Cloud-based Gemini models

### Document Processing
- **PyPDF2** — PDF text extraction
- **python-docx** — Word document parsing
- **Pillow** — Image processing

### Security & Utilities
- **Cryptography** — Data encryption
- **Keyring** — Secure credential storage
- **Portalocker** — File locking and concurrency

### Backend (Optional)
- **PHP 7.4+** — Web server (server-php-auth)
- **MySQL 5.7+** — Database backend
- **JWT** — Token-based authentication

---

## Project Structure

```
ai-document-analyzer/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.json                        # Default configuration template
│
├── main.py                            # Application entry point
├── main_window.py                     # Core application logic & AI integration
├── settings_window.py                 # Settings/configuration dialog
├── ui_main_window.py                  # PyQt6 UI definitions (auto-generated)
├── ui_settings_window.py              # Settings UI definitions (auto-generated)
│
├── large_doc_manager.py               # Large doc processing, RAG, vector store
├── lock_manager.py                    # Remote lock system (Google Sheets polling)
├── lock_overlay.py                    # Full-screen lock UI overlay
├── auth.py                            # Local authentication logic
├── login_dialog.py                    # Login dialog UI
├── login_overlay.py                   # Login overlay UI
├── startup_helper.py                  # Pre-launch initialization
├── offline_bootstrap.py               # Offline functionality setup
│
├── styles.qss                         # Global application stylesheet
├── prompts.txt                        # AI prompt templates
├── update_all_prompts.py              # Utility to update prompts
│
├── assets/                            # Icons, images, resources
├── resources.qrc                      # Qt resource file
│
├── build_complete.bat                 # Complete build + installer script (Windows)
├── build_exe.bat                      # Build executable only (Windows)
├── build_debug.bat                    # Debug build (Windows)
├── installer.nsi                      # NSIS installer configuration
├── AI Document Analyzer.spec          # PyInstaller spec for executable
├── create_icon.py                     # Icon generation script
│
├── Documentation files:
├── LARGE_DOC_GUIDE.md                 # Large document & OCR processing guide
├── LOCK_SYSTEM_GUIDE.md               # Remote lock system guide
├── PYTHON_3.11_MIGRATION.md           # Python version & setup guide
├── README_Windows_Deployment.md       # Windows deployment details
│
└── server-php-auth/                   # Optional enterprise authentication backend
    ├── config.sample.php              # Backend configuration template
    ├── schema.sql                     # Database schema
    ├── seed_admin.php                 # Admin user seeding script
    ├── src/
    │   ├── auth.php                   # Authentication logic
    │   ├── db.php                     # Database connection
    │   ├── jwt.php                    # JWT token handling
    │   ├── util.php                   # Utility functions
    │   ├── RefreshTokenRepository.php # Token persistence
    │   └── controllers/
    │       ├── AuthController.php     # Login/logout/refresh endpoints
    │       └── AdminController.php    # User management (admin-only)
    │   └── repositories/
    │       └── UserRepository.php     # Database user operations
    └── public/
        ├── index.php                  # Main API entry point
        └── admin/
            ├── app.js                 # Admin panel JavaScript
            ├── dashboard.html         # User management dashboard
            └── login.html             # Admin login page
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `main_window.py` | Core business logic: document processing, AI interactions, UI coordination |
| `large_doc_manager.py` | Handles vector store (Qdrant), chunking, embeddings, and RAG queries |
| `lock_manager.py` | Polls Google Sheet every 60s to check if app should be locked remotely |
| `auth.py` | Local user authentication handling |
| `prompts.txt` | Stores AI prompts for summarization (English/Arabic variants) |

---

## Installation & Setup

### Prerequisites

- **Windows 10/11** (64-bit), Linux, or macOS
- **Python 3.8 or higher** (3.11+ recommended)
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/AsadAliQuant/ai-document-analyzer.git
cd ai-document-analyzer

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
```

### Detailed Setup

#### 1. Create Virtual Environment

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- **PyQt6** — Desktop UI framework
- **Ollama client** — Local AI model integration
- **LangChain** — Document processing and RAG
- **Qdrant client** — Vector database
- **Sentence Transformers** — Embeddings
- **EasyOCR** — Image text extraction
- **PyTorch** — Deep learning backend
- **Google Generative AI** — Cloud AI integration
- And all other dependencies

#### 3. Verify Installation

```bash
# Test core imports
python -c "from PyQt6.QtWidgets import QApplication; print('✓ PyQt6')"
python -c "from qdrant_client import QdrantClient; print('✓ Qdrant')"
python -c "from sentence_transformers import SentenceTransformer; print('✓ Sentence Transformers')"
python -c "from easyocr import Reader; print('✓ EasyOCR')"
python -c "import torch; print(f'✓ PyTorch (CUDA: {torch.cuda.is_available()})')"
```

#### 4. First Run

```bash
python main.py
```

On first run, the application will:
- Create configuration directory: `%APPDATA%/AI Document Analyzer/`
- Download OCR and embedding models (~100-200 MB)
- Initialize Qdrant vector database
- Create default configuration

---

## Configuration

### Configuration File

The application stores configuration at:
- **Windows**: `%APPDATA%/AI Document Analyzer/config.json`
- **Linux**: `~/.config/AI Document Analyzer/config.json`
- **macOS**: `~/Library/Application Support/AI Document Analyzer/config.json`

### config.json Structure

```json
{
  "GOOGLE_API_KEY": "",
  "API_BASE_URL": "https://ssma.sa/ai_api",
  "EMBEDDING_MODEL": "nomic-embed-text",
  "LANGUAGE": "en"
}
```

### Setting Up Ollama (Offline)

1. **Install Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Install and start the Ollama service

2. **Download a Model**
   ```bash
   ollama pull llama2
   # or for smaller:
   ollama pull mistral
   ```

3. **Verify Ollama is Running**
   ```bash
   # Should respond with model list
   curl http://localhost:11434/api/tags
   ```

4. **Configure in Application**
   - Open Settings in the app
   - Select "Offline (Ollama)" as AI backend
   - Ensure "ollama pull llama2" completed successfully

### Setting Up Google Gemini (Online)

1. **Get API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Copy the key

2. **Configure in Application**
   - Open Settings in the app
   - Paste your API key in the Google API Key field
   - Select "Online (Google Gemini)" as AI backend
   - Save settings

### Embedding Model Configuration

The application uses `sentence-transformers/all-MiniLM-L6-v2` for semantic embeddings:

- **Lightweight**: ~90 MB model size
- **Fast**: Quick inference on CPU or GPU
- **Accurate**: Optimized for semantic similarity
- **Offline**: Works completely offline

To use a different model, edit `large_doc_manager.py`:

```python
self.embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
```

---

## Features in Detail

### Large Document & Image Processing

#### How It Works

The application automatically detects documents that are too large for direct AI processing and uses an intelligent **Retrieval-Augmented Generation (RAG)** pipeline:

1. **Automatic Detection**
   - Documents with >2 pages are flagged as "large"
   - All images (PNG, JPG, JPEG) are processed with OCR

2. **Processing Pipeline**
   ```
   Document/Image → OCR (if image) → Chunking → Embeddings → Vector Store → RAG
   ```

3. **Chunking & Embedding**
   - Text split into 1200-character chunks with 200-character overlap
   - Each chunk embedded using all-MiniLM-L6-v2 model
   - Embeddings stored in Qdrant vector database

4. **RAG for Q&A**
   - User question is embedded
   - Similar chunks retrieved based on semantic similarity
   - Retrieved context passed to AI model
   - Model generates answer based on document content

#### OCR for Images

**EasyOCR** extracts text from images:

- **Languages**: English and Arabic support built-in
- **GPU Acceleration**: Automatic CUDA when available
- **Local Processing**: All OCR happens on your device
- **First Run**: Downloads model (~100 MB per language)

```bash
# Test OCR manually
python -c "from easyocr import Reader; reader = Reader(['en']); print('✓ OCR Ready')"
```

#### Storage Location

Vector stores are saved in:
- **Windows**: `%APPDATA%/AI Document Analyzer/vector_store/`
- **Linux**: `~/.config/AI Document Analyzer/vector_store/`

Each document gets a unique identifier based on file path, size, and modification time for reliable caching.

#### Benefits

| Feature | Benefit |
|---------|---------|
| **Unlimited Document Size** | Handle gigabyte-scale documents |
| **Context-Aware Q&A** | Answers based on actual document content |
| **Fast Reloading** | Previously processed docs load instantly |
| **Complete Privacy** | No document content sent externally (with Ollama) |
| **GPU Support** | Significantly faster processing with CUDA |

---

### Remote Lock System

A lightweight feature to remotely disable the application by updating a public **Google Sheet**.

#### How It Works

1. **Setup Google Sheet**
   - Create a public Google Sheet
   - Make cell A1 control the lock state:
     - `0` = Unlocked (normal operation)
     - `1` = Locked (blocks all access)

2. **Application Polling**
   - App checks the sheet every 60 seconds
   - If A1 is `1`, full-screen blocking overlay appears
   - User cannot interact with application

3. **Offline Behavior**
   - Last known state cached locally in `cache.txt`
   - If offline, uses cached state
   - When online again, fetches latest state

4. **User Experience When Locked**
   ```
   ╔════════════════════════════════════════╗
   ║                                        ║
   ║   This application is temporarily     ║
   ║   disabled.                           ║
   ║                                        ║
   ║   Please contact the developer.       ║
   ║                                        ║
   ║        [ OK ]                         ║
   ║                                        ║
   ╚════════════════════════════════════════╝
   ```

#### Customization

**Change Lock Check Interval** (`lock_manager.py`):
```python
self.timer.start(60000)  # milliseconds (default: 60 seconds)
```

**Change Lock Message** (`lock_overlay.py`):
```python
message = QLabel("Your custom message here")
```

**Change Check URL** (`main_window.py`):
```python
self.lock_manager = LockManager(csv_url="YOUR_NEW_URL_HERE")
```

#### Testing the Lock System

1. Open your Google Sheet
2. Set cell A1 to `1`
3. Wait up to 60 seconds
4. App should show lock overlay
5. Change A1 back to `0`
6. Wait up to 60 seconds
7. Overlay should disappear

---

### Vector Database & Persistence

#### Qdrant

The application uses **Qdrant** as its vector database:

**Key Features:**
- ✅ **Embedded**: No external server required—runs in-process
- ✅ **Fast**: ~100-1000 queries per second
- ✅ **Persistent**: Data saved to disk automatically
- ✅ **Scalable**: Handles millions of vectors efficiently
- ✅ **Compatible**: Works with Python 3.8-3.13+

**Storage Details:**
- Vector data stored in `%APPDATA%/AI Document Analyzer/vector_store/`
- One database per document/image
- Automatic cleanup available via Settings

#### Clearing Vector Store

To remove all stored vector data:

```bash
# Option 1: Through application
# Settings → Clear Vector Store → Confirm

# Option 2: Manual (close app first)
rm -r "%APPDATA%/AI Document Analyzer/vector_store"  # Windows
rm -rf ~/.config/AI\ Document\ Analyzer/vector_store  # Linux
rm -rf ~/Library/Application\ Support/AI\ Document\ Analyzer/vector_store  # macOS
```

---

## Building for Distribution

### Windows Executable

Build a standalone .exe with PyInstaller:

```bash
pip install pyinstaller

# Simple build
pyinstaller "AI Document Analyzer.spec"

# Output: dist/AI Document Analyzer.exe (~80-100 MB)
```

### Windows Installer

Create a professional installer with NSIS:

```bash
# Requires NSIS to be installed
build_complete.bat

# Output: AI_Document_Analyzer_Setup.exe
```

**Installer Features:**
- ✅ Desktop shortcut
- ✅ Start menu entry
- ✅ Uninstaller
- ✅ Windows registry integration

**On First Run, User Will See:**
- License agreement
- Installation directory selection
- Shortcuts creation

### Distribution Package

For public release:

```
├── AI_Document_Analyzer_Setup.exe    (~30-50 MB) — Windows installer
├── README.md                         — This guide
└── CHANGELOG.md                      — Version history
```

**Requirements for End Users:**
- Windows 10/11 (64-bit)
- No additional software required
- For Ollama: Install Ollama separately + download models

---

## Server-PHP-Auth Backend

### Purpose

**Optional** enterprise-grade authentication backend enabling:
- Centralized user management
- JWT token-based authentication
- Role-based access control (RBAC)
- Admin dashboard for user management
- User status tracking

**Important**: The desktop application works perfectly **standalone without this backend**. It's only needed for enterprise deployments requiring:
- Multiple users
- Centralized control
- Audit logging
- User lifecycle management

### Architecture

```
┌─────────────────────┐
│  Desktop App        │
│  (PyQt6)            │
└──────────┬──────────┘
           │ HTTPS/JWT
           ▼
┌─────────────────────┐
│  PHP Backend        │
│  (server-php-auth)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MySQL Database     │
│  (users, tokens)    │
└─────────────────────┘
```

### Components

#### AuthController.php — Authentication Endpoints

```php
POST   /api/auth/login        # User login → returns JWT token
POST   /api/auth/refresh      # Refresh expired token
POST   /api/auth/logout       # Invalidate refresh token
```

**Login Request/Response:**
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

#### AdminController.php — User Management (Admin-Only)

```php
GET    /api/admin/users                      # List all users
POST   /api/admin/users                      # Create new user
PUT    /api/admin/users/{userId}             # Update user
DELETE /api/admin/users/{userId}             # Delete user
PUT    /api/admin/users/{userId}/status      # Enable/disable user
```

#### UserRepository.php — Database Operations

- User CRUD operations
- Password hashing (bcrypt)
- Status tracking (active/disabled)
- Last login timestamp

### Database Schema

#### users Table
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  role ENUM('user', 'admin') DEFAULT 'user',
  status ENUM('active', 'disabled') DEFAULT 'active',
  last_login DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### refresh_tokens Table
```sql
CREATE TABLE refresh_tokens (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  token_hash VARCHAR(255) UNIQUE NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### JWT Token System

#### Access Token
- **TTL**: 15 minutes
- **Purpose**: Authenticate API requests
- **Claim**: User ID, email, role

#### Refresh Token
- **TTL**: 30 days
- **Purpose**: Obtain new access tokens
- **Issued**: During login
- **Hashed**: Stored in database

**Refresh Flow:**
```
1. Access token expires
2. Desktop app sends refresh token
3. Backend validates and generates new access token
4. App continues using new token
```

### Configuration

Edit `config.sample.php`:

```php
// Database
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', 'password');
define('DB_NAME', 'ai_analyzer');

// JWT
define('JWT_SECRET', 'your-secret-key-min-32-chars');
define('JWT_ALGORITHM', 'HS256');
define('ACCESS_TOKEN_TTL', 900);      // 15 minutes
define('REFRESH_TOKEN_TTL', 2592000); // 30 days

// Initial Admin
define('SEED_TOKEN', 'temp-token-for-first-admin-creation');
define('INITIAL_ADMIN_EMAIL', 'admin@example.com');
```

### Deployment

1. **Copy to Web Server**
   ```bash
   cp -r server-php-auth/* /var/www/html/ai-api/
   ```

2. **Setup Database**
   ```bash
   mysql -u root -p < server-php-auth/schema.sql
   ```

3. **Create Initial Admin**
   ```bash
   php server-php-auth/seed_admin.php
   ```

4. **Configure Desktop App**
   - Set `API_BASE_URL` in config.json
   - Users will see login screen before accessing app

### Features

| Feature | Details |
|---------|---------|
| **Role-Based Access** | Separate user and admin roles |
| **User Status** | Enable/disable users without deletion |
| **Last Login** | Track user access for audit trails |
| **Secure Passwords** | bcrypt hashing |
| **Token Refresh** | Seamless token renewal without re-login |
| **Logout** | Invalidate refresh tokens on logout |

### Desktop App Integration

When backend is configured in `config.json`:

1. **Login Screen**: Users must authenticate before accessing app
2. **Token Management**: Automatic refresh before expiration
3. **Admin Controls**: Admins see additional management options
4. **Access Control**: Standard users can't access admin features

---

## AI Models & Prompts

### Ollama (Offline)

**Best For**: Privacy, offline operation, complete data control

```bash
# Install Ollama
# Download from: https://ollama.ai

# Pull a model
ollama pull llama2         # 7B parameters, ~4GB
ollama pull mistral        # 7B parameters, ~5GB (faster)
ollama pull llama2-13b     # 13B parameters, ~8GB (more capable)
```

**Configuration**:
- Model runs locally on `localhost:11434`
- No internet connection required
- No API keys needed
- All data stays on your machine

### Google Gemini (Online)

**Best For**: Higher quality, multi-modal capabilities, no infrastructure mgmt

```
1. Get API key from: https://makersuite.google.com/app/apikey
2. Paste in Settings → Google API Key
3. Select "Online (Gemini)" backend
```

**Configuration**:
- Requires internet connection
- Uses Google's Gemini models
- Data sent to Google servers
- Requires valid API key

### Prompt Templates

Prompts are stored in `prompts.txt` in both English and Arabic:

**Summarization Prompt Structure:**
```
Input: [Document Text]
Output: JSON with:
  - key_points: Critical findings
  - methods: Approaches used
  - conclusions: Final summary
```

Update prompts programmatically:
```bash
python update_all_prompts.py
```

### Quality Comparison

| Aspect | Ollama | Gemini |
|--------|--------|--------|
| **Privacy** | ✅ Complete | ⚠️ Sent to Google |
| **Offline** | ✅ Yes | ❌ No |
| **Speed** | ⚠️ Slower (CPU) | ✅ Fast |
| **Quality** | ✅ Good | ✅✅ Excellent |
| **Cost** | ✅ Free | ⚠️ Usage charges |

---

## Multi-Language Support

### Supported Languages

- **English** — Full support
- **Arabic** — Full support (UI & OCR)

### UI Language

Settings → Language → Select English/Arabic

### OCR Language

Automatically detects and processes text in:
- **Arabic Script**: Full support
- **Latin Script**: Full support
- **Mixed**: Both handled in same document

### Prompts

Summarization prompts are localized:
- Arabic-specific prompts for Arabic documents
- English-specific prompts for English documents
- Maintains semantic quality across languages

---

## Security & Privacy

### Privacy Features

✅ **Offline Operation**
- Run completely offline with Ollama backend
- No internet connection required
- No telemetry, no tracking

✅ **Local Processing**
- All documents processed locally
- No cloud uploads of document content
- Vector embeddings generated locally

✅ **OCR Privacy**
- EasyOCR runs locally
- No cloud image processing
- Images never uploaded

✅ **Credential Security**
- Passwords stored in system keyring
- API keys never logged
- Credentials not saved to disk

### Security Features

🔐 **Encryption**
- Cryptography library for data protection
- Optional AES encryption for sensitive files

🔐 **Authentication**
- JWT token system (with backend)
- Multi-user support via server-php-auth
- Role-based access control

🔐 **Remote Control**
- Lock system for emergency disable
- User retains control via Google Sheet
- Cached state for offline lockout

---

## GPU Acceleration

### CUDA Support

The application automatically detects and uses NVIDIA CUDA when available:

```python
# Auto-detection during startup
import torch
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
```

### GPU-Accelerated Components

1. **Embeddings** — Sentence-transformers with CUDA
2. **OCR** — EasyOCR with CUDA
3. **Deep Learning** — PyTorch with CUDA

### Performance Comparison

| Operation | CPU (No GPU) | GPU (CUDA) |
|-----------|-------------|-----------|
| Embedding 1000 chunks | ~30 seconds | ~2 seconds |
| OCR on image | ~5 seconds | ~0.5 seconds |
| First-time setup | ~5 minutes | ~30 seconds |

### Enabling CUDA

```bash
# For NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"  # Should print: True
```

### Requirements

- **NVIDIA GPU** with compute capability 3.5+
- **NVIDIA CUDA Toolkit** installed
- **cuDNN** (usually auto-installed with PyTorch)

---

## Troubleshooting

### Installation Issues

**"ModuleNotFoundError: No module named 'PyQt6'"**
```bash
pip install PyQt6>=6.6
pip install -r requirements.txt
```

**"Qdrant is not available"**
```bash
pip install qdrant-client>=1.7.0
```

**"torch is not available"**
```bash
# CPU-only
pip install torch torchvision torchaudio

# CUDA GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Runtime Issues

**"Ollama not available"**
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Start the Ollama service
3. Verify: `curl http://localhost:11434/api/tags`
4. Re-run application

**"EasyOCR not installed"**
```bash
pip install easyocr>=1.7.0 Pillow>=10.0.0
```

**"Failed to extract text from image"**
- Verify image is not corrupted
- Ensure text is clearly visible
- Check image resolution (very low-res images may fail)
- Try a different image format

**"Missing Google API key"**
1. Get key from [AI Studio](https://makersuite.google.com/app/apikey)
2. Open Settings → API Keys
3. Paste Google API key
4. Save and restart

### Performance Issues

**"Slow OCR processing"**
- First run downloads models (~100 MB)
- CPU-only OCR is slow; install CUDA for GPU acceleration
- Restarting the app clears memory

**"Slow document processing"**
- First-time chunking can take time for large documents
- Subsequent loads are instant (cached)
- GPU significantly speeds up embeddings

**"High memory usage"**
- Large documents may temporarily use memory during chunking
- Vector store limited to ~500MB per document
- Close other applications

### Vector Store Issues

**"Vector store corrupted"**
```bash
# Clear and rebuild
# Close application first
rm -r "%APPDATA%/AI Document Analyzer/vector_store"
# Restart app and reprocess documents
```

**"Can't find previously processed document"**
- If file was moved/renamed, vector store cache is invalidated
- Re-process document from new location
- Old vector store can be manually deleted

---

## FAQ

### Python & Version Compatibility

**Q: What Python versions are supported?**
A: Python 3.8 through 3.13+. Version 3.11+ recommended for best compatibility.

**Q: Can I use Python 3.7 or older?**
A: No. PyQt6 requires Python 3.8+.

**Q: Do I need Anaconda?**
A: No. Standard Python with venv works fine.

### Offline vs. Online Operation

**Q: Can I run this completely offline?**
A: Yes, with Ollama backend. Download models while online, then run offline.

**Q: Which backend is faster?**
A: Gemini API is faster but requires internet. Ollama may be slower but ensures privacy.

**Q: Can I switch between Ollama and Gemini?**
A: Yes, anytime via Settings → AI Backend.

### Model Storage & Size

**Q: Where are AI models stored?**
A:
- **Ollama**: `~/.ollama/models/`
- **Embeddings**: `~/.cache/huggingface/hub/`
- **OCR**: `~/.EasyOCR/model/`

**Q: How much disk space do I need?**
A:
- BaseApplication: ~500 MB
- LLaMA 7B model: ~4 GB
- Embeddings + OCR: ~200 MB
- Plus vector store size (varies by documents)

**Q: How long do models take to download?**
A: Depends on internet speed:
- LLaMA 7B: ~10-30 minutes
- Embeddings: ~2-5 minutes
- OCR: ~5-10 minutes

### Document Processing

**Q: What's the maximum document size?**
A: Technically unlimited. RAG handles any size efficiently.

**Q: How many documents can I process?**
A: Unlimited. Vector store grows with each document.

**Q: Can I delete processed documents?**
A: Yes, via Settings → Clear Vector Store (clears all) or manually delete from `vector_store/` folder.

**Q: What file formats are supported?**
A:
- **Documents**: PDF, DOCX, TXT
- **Images**: PNG, JPG, JPEG
- **Text Input**: Direct paste/typing

### Remote Lock System

**Q: Does the lock system work offline?**
A: Yes, uses cached last-known state if Internet unavailable.

**Q: How quickly do lock changes take effect?**
A: Within 60 seconds (polling interval).

**Q: Can I customize the lock message?**
A: Yes, edit `lock_overlay.py` line 25.

### Server Backend

**Q: Do I need the server-php-auth backend?**
A: No, it's optional. Desktop app works standalone.

**Q: When should I use the backend?**
A: For enterprise deployments requiring:
- Multiple users with individual credentials
- Centralized user management
- Role-based access control
- Audit logging

**Q: Can I deploy the backend without the desktop app?**
A: The server is designed specifically for this app, but technically the APIs are REST-based.

---

## Development

### Running from Source

```bash
# Clone repository
git clone https://github.com/yourusername/ai-document-analyzer.git

# Setup environment
cd ai-document-analyzer
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt

# Run
python main.py
```

### Building Executable

```bash
pip install pyinstaller
pyinstaller "AI Document Analyzer.spec"
# Output: dist/AI Document Analyzer.exe
```

### Creating Installer (Windows)

```bash
# Requires NSIS to be installed
build_complete.bat
# Output: AI_Document_Analyzer_Setup.exe
```

---

## Contributing

Contributions are welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Test on both Ollama and Gemini backends
- Test with both English and Arabic
- Document significant changes
- Update CHANGELOG.md

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

**You are free to:**
- ✅ Use for commercial purposes
- ✅ Modify and redistribute
- ✅ Use privately

**You must:**
- ⚠️ Include license and copyright notice

---

## Support

### Getting Help

- 📖 **Documentation**: See [LARGE_DOC_GUIDE.md](LARGE_DOC_GUIDE.md), [LOCK_SYSTEM_GUIDE.md](LOCK_SYSTEM_GUIDE.md), [PYTHON_3.11_MIGRATION.md](PYTHON_3.11_MIGRATION.md)

### System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11, Linux, macOS |
| **Python** | 3.8+ (3.11+ recommended) |
| **RAM** | 8 GB minimum (16 GB for large documents) |
| **Disk** | 2 GB minimum + model storage |
| **GPU** | Optional (NVIDIA CUDA for acceleration) |

### Performance Tips

1. **Use GPU**: Install CUDA for 10-20x faster processing
2. **Close Browsers**: Free up RAM for embeddings/OCR
3. **SSD Storage**: Faster vector store access
4. **Dedicated GPU**: If processing many large documents
5. **Ollama Models**: Start with 7B parameter models (llama2, mistral)

---

## Roadmap

Planned features and improvements:
- [ ] Multi-language UI (Spanish, French, German)
- [ ] Web-based interface
- [ ] Document comparison and diff
- [ ] Export to other formats (DOCX, XLSX)
- [ ] Batch processing
- [ ] Custom fine-tuned models
- [ ] Mobile app

---

## Changelog

### Version 1.0.0 (Latest)
- ✨ Initial release
- 📄 PDF, DOCX, TXT support
- 🖼️ Image OCR with EasyOCR
- 🔄 RAG for intelligent Q&A
- 🔒 Remote lock system
- 🇬🇧 English/Arabic support
- 🚀 Ollama + Google Gemini backends

---

## Acknowledgments

- **PyQt6** — For the excellent UI framework
- **LangChain** — For document processing utilities
- **Qdrant** — For embedded vector database
- **EasyOCR** — For local OCR capabilities
- **Ollama** — For offline LLaMA inference
- **Google Generative AI** — For cloud AI integration

---

Last Updated: March 2026
