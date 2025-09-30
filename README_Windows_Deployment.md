build# AI Document Analyzer - Windows Desktop Application

## Overview
This is a PyQt6-based desktop application for AI-powered document analysis, supporting both offline (Ollama) and online (Google Gemini) AI models.

## Building the Windows Application

### Prerequisites
- Python 3.8+ installed
- All dependencies from `requirements.txt`
- PyInstaller (installed automatically by build scripts)
- NSIS (optional, for creating installer)

### Quick Build
1. Run `build_complete.bat` for a complete build with installer
2. Or run `build_windows.bat` for just the executable

### Manual Build Steps
```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build executable
pyinstaller "AI Document Analyzer.spec"
```

## Distribution Files

### Executable Only
- **Location**: `dist/AI Document Analyzer.exe`
- **Size**: ~50-100 MB (includes all dependencies)
- **Requirements**: None (standalone executable)

### Windows Installer
- **Location**: `AI_Document_Analyzer_Setup.exe` (after running build_complete.bat)
- **Features**: 
  - Desktop shortcut
  - Start menu entry
  - Uninstaller
  - Windows registry integration

## Application Features

### Supported File Types
- **Documents**: PDF, DOCX, TXT
- **Images**: PNG, JPG, JPEG
- **Text Input**: Direct paste/typing

### AI Models
- **Offline**: Ollama with LLaMA models
- **Online**: Google Gemini models

### Key Features
- Document text extraction
- AI-powered summarization
- Q&A chat interface
- PDF export
- Multi-language support (English/Arabic)
- System tray integration

## Installation Requirements

### For End Users
- Windows 10/11 (64-bit)
- No additional software required (standalone executable)

### For Ollama Integration
- Ollama installed and running
- LLaMA models downloaded via Ollama
- For large document processing: Embedding model (default: `nomic-embed-text`, configurable in Settings)

### For Gemini Integration
- Google API key (configured in settings)

## Configuration

### First Run
- Application creates config directory: `%APPDATA%/AI Document Analyzer/`
- Copies `config.json` from installation directory if present

### Settings
- Access via Settings button in application
- Configure API keys and preferences
- Configure embedding model for large document processing
- Language selection (English/Arabic)

## Troubleshooting

### Common Issues
1. **"Ollama not available"**: Install Ollama and start the service
2. **"Missing API key"**: Add Google API key in Settings
3. **File extraction errors**: Ensure file is not corrupted or password-protected

### Logs
- Application logs are stored in `%APPDATA%/AI Document Analyzer/`
- Check Windows Event Viewer for system-level issues

## Development

### Project Structure
```
app_gptUI/
├── main.py                 # Application entry point
├── main_window.py          # Main application logic
├── settings_window.py      # Settings dialog
├── ui_main_window.py       # UI definitions
├── ui_settings_window.py   # Settings UI
├── assets/                 # Icons and images
├── styles.qss             # Application styling
├── config.json            # Default configuration
├── requirements.txt       # Python dependencies
├── AI Document Analyzer.spec  # PyInstaller configuration
└── build scripts          # Build automation
```

### Building for Distribution
1. Test the application thoroughly
2. Update version numbers in installer.nsi
3. Run `build_complete.bat`
4. Test the installer on a clean Windows system
5. Distribute `AI_Document_Analyzer_Setup.exe`

## License
[Add your license information here]

## Support
[Add support contact information here]
