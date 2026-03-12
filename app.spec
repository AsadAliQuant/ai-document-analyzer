# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI Document Analyzer
Bundles all dependencies into a single EXE for Windows 10/11
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
    'scipy',
    'sklearn',
    'imageio',
    'networkx',
    'tifffile',
    'lazy_loader',
    'pooch',
]

for pkg in packages_to_collect:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception as e:
        print(f"Warning: Could not collect {pkg}: {e}")

# Additional submodules that might be missed
extra_submodules = [
    'langchain_community.vectorstores',
    'langchain_community.embeddings',
    'langchain_huggingface.embeddings',
    'qdrant_client.models',
    'qdrant_client.http',
    'qdrant_client.http.models',
    'grpc._cython',
    'google.protobuf',
    'google.auth',
    'scipy',
    'scipy.special',
    'sklearn',
    'sklearn.utils',
    'sklearn.neighbors',
    'tqdm',
    'filelock',
    'regex',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'httpx',
    'httpcore',
    'anyio',
    'sniffio',
    'h11',
    'pydantic',
    'pydantic_core',
    'typing_extensions',
    'annotated_types',
]

for submod in extra_submodules:
    try:
        hiddenimports += collect_submodules(submod)
    except Exception:
        hiddenimports.append(submod)

# Explicit hidden imports for tricky modules
explicit_hiddenimports = [
    'langchain_text_splitters',
    'langchain_text_splitters.character',
    'langchain_text_splitters.base',
    'langchain_text_splitters.rec',
    'langchain_text_splitters.text_splitter',
    'langchain.text_splitter',
    'langchain.schema',
    'langchain_core',
    'langchain_core.documents',
    'langchain_core.documents.base',
    'langchain_core.pydantic_v1',
    'sentence_transformers',
    'sentence_transformers.models',
    'sentence_transformers.util',
    'transformers',
    'transformers.models',
    'transformers.tokenization_utils_base',
    'huggingface_hub',
    'huggingface_hub.hf_api',
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torchvision',
    'easyocr',
    'easyocr.easyocr',
    'easyocr.recognition',
    'easyocr.detection',
    'easyocr.craft',
    'easyocr.craft_utils',
    'easyocr.imgproc',
    'easyocr.utils',
    'easyocr.config',
    'easyocr.model',
    'easyocr.model.vgg_model',
    'easyocr.model.modules',
    'easyocr.trainer',
    'easyocr.character',
    'skimage',
    'skimage.transform',
    'skimage.io',
    'skimage.color',
    'skimage.filters',
    'skimage.morphology',
    'skimage.feature',
    'skimage._shared',
    'skimage._shared.geometry',
    'skimage.util',
    'skimage.util.dtype',
    'imageio',
    'imageio.core',
    'imageio.plugins',
    'cv2',
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib',
    'numpy.lib.format',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'qdrant_client',
    'qdrant_client.local',
    'qdrant_client.qdrant_local',
    'sqlite3',
    'pkg_resources',
    'pkg_resources.extern',
    'jaraco',
    'jaraco.classes',
    'jaraco.functools',
    'jaraco.context',
    'keyring',
    'keyring.backends',
    'keyring.backends.Windows',
    'win32timezone',
    'pythoncom',
    'pywintypes',
    'win32api',
    'win32con',
    'win32cred',
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

# Remove duplicates
hiddenimports = list(set(hiddenimports))

# Add application data files (only if they exist)
app_datas = []

if os.path.isdir('assets'):
    app_datas.append(('assets', 'assets'))

if os.path.isfile('styles.qss'):
    app_datas.append(('styles.qss', '.'))

if os.path.isfile('config.json'):
    app_datas.append(('config.json', '.'))

if os.path.isfile('prompts.txt'):
    app_datas.append(('prompts.txt', '.'))

# Add models directory if it exists and has content
if os.path.isdir('models') and os.listdir('models'):
    app_datas.append(('models', 'models'))

datas += app_datas

# Print what we're including for debugging
print(f"Including {len(hiddenimports)} hidden imports")
print(f"Including {len(app_datas)} application data items: {[d[0] for d in app_datas]}")

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_imports.py'],
    excludes=[
        'matplotlib',
        'tkinter',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'PyQt5',  # Exclude PyQt5 if using PyQt6
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI Document Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico' if os.path.exists('assets/logo.ico') else None,
)
