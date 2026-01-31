# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI Document Analyzer - FOLDER MODE
Creates a folder with all dependencies (more reliable than single EXE)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Collect all data and binaries for key packages
datas = []
binaries = []
hiddenimports = []

# Core packages that need full collection
packages_to_collect = [
    'PyQt6',
    'langchain',
    'langchain_core',
    'langchain_community',
    'langchain_text_splitters',
    'langchain_huggingface',
    'sentence_transformers',
    'transformers',
    'huggingface_hub',
    'tokenizers',
    'safetensors',
    'torch',
    'torchvision',
    'numpy',
    'scipy',
    'sklearn',
    'qdrant_client',
    'grpc',
    'grpcio',
    'easyocr',
    'skimage',
    'scikit-image',
    'imageio',
    'cv2',
    'PIL',
    'Pillow',
    'PyPDF2',
    'docx',
    'ollama',
    'google',
    'google.generativeai',
    'google.ai',
    'keyring',
    'jaraco',
    'requests',
    'cryptography',
]

for pkg in packages_to_collect:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception as e:
        print(f"Warning: Could not collect {pkg}: {e}")

# Additional submodules
extra_submodules = [
    'langchain_community.vectorstores',
    'langchain_community.embeddings',
    'langchain_huggingface.embeddings',
    'qdrant_client.models',
    'qdrant_client.http',
    'scipy.stats',
    'scipy.special',
    'scipy.linalg',
    'sklearn.utils',
    'sklearn.neighbors',
    'sklearn.metrics',
]

for submod in extra_submodules:
    try:
        hiddenimports += collect_submodules(submod)
    except Exception:
        hiddenimports.append(submod)

# Explicit hidden imports
explicit_hiddenimports = [
    'langchain_text_splitters',
    'langchain_text_splitters.character',
    'easyocr',
    'easyocr.easyocr',
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'qdrant_client',
    'sqlite3',
    'keyring',
    'keyring.backends',
    'keyring.backends.Windows',
    'offline_bootstrap',
    'startup_helper',
    'large_doc_manager',
    'lock_manager',
    'lock_overlay',
    'login_overlay',
    'login_dialog',
    'settings_window',
    'auth',
    'ui_main_window',
    'ui_settings_window',
]

hiddenimports += explicit_hiddenimports
hiddenimports = list(set(hiddenimports))

# Add application data files
app_datas = []
if os.path.isdir('assets'):
    app_datas.append(('assets', 'assets'))
if os.path.isfile('styles.qss'):
    app_datas.append(('styles.qss', '.'))
if os.path.isfile('config.json'):
    app_datas.append(('config.json', '.'))
if os.path.isfile('prompts.txt'):
    app_datas.append(('prompts.txt', '.'))
if os.path.isdir('models') and os.listdir('models'):
    app_datas.append(('models', 'models'))

datas += app_datas

print(f"Including {len(hiddenimports)} hidden imports")

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],  # No runtime hooks - they cause issues
    excludes=[
        'matplotlib',
        'tkinter',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'PyQt5',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE for folder mode (not bundled)
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - binaries go to COLLECT
    exclude_binaries=True,  # Important for folder mode
    name='AI Document Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX for reliability
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico' if os.path.exists('assets/logo.ico') else None,
)

# COLLECT creates the folder with all files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AI Document Analyzer',
)
