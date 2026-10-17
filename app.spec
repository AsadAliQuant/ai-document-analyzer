# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller single-file build for AI Document Analyzer."""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules


block_cipher = None
datas = []
binaries = []
hiddenimports = []

packages_to_collect = [
    "langchain_core",
    "langchain_text_splitters",
    "qdrant_client",
    "PyPDF2",
    "docx",
    "ollama",
    "google.genai",
    "keyring",
    "cryptography",
]

for package in packages_to_collect:
    try:
        package_datas, package_binaries, package_hiddenimports = collect_all(package)
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hiddenimports
    except Exception as exc:
        print(f"Warning: Could not collect {package}: {exc}")

for submodule in [
    "qdrant_client.models",
    "qdrant_client.http",
    "qdrant_client.http.models",
    "grpc._cython",
    "google.protobuf",
    "google.auth",
    "requests",
    "urllib3",
    "certifi",
    "charset_normalizer",
    "httpx",
    "httpcore",
    "anyio",
    "sniffio",
    "h11",
    "pydantic",
    "pydantic_core",
    "typing_extensions",
    "annotated_types",
]:
    try:
        hiddenimports += collect_submodules(submodule)
    except Exception:
        hiddenimports.append(submodule)

hiddenimports += [
    "langchain_text_splitters",
    "langchain_text_splitters.character",
    "langchain_text_splitters.base",
    "langchain_core.documents",
    "google.genai",
    "google.genai.types",
    "numpy",
    "qdrant_client",
    "qdrant_client.local",
    "qdrant_client.qdrant_local",
    "sqlite3",
    "pkg_resources",
    "jaraco",
    "jaraco.classes",
    "jaraco.functools",
    "jaraco.context",
    "keyring",
    "keyring.backends",
    "keyring.backends.Windows",
    "win32timezone",
    "pythoncom",
    "pywintypes",
    "win32api",
    "win32con",
    "win32cred",
    "gemini_fallback",
    "gemini_ocr",
    "startup_helper",
    "large_doc_manager",
    "lock_manager",
    "lock_overlay",
    "login_overlay",
    "login_dialog",
    "settings_window",
    "auth",
    "ui_main_window",
    "ui_settings_window",
]
hiddenimports = list(set(hiddenimports))

for source, destination in [
    ("assets", "assets"),
    ("styles.qss", "."),
    ("config.json", "."),
    ("prompts.txt", "."),
]:
    if os.path.isdir(source) or os.path.isfile(source):
        datas.append((source, destination))

print(f"Including {len(hiddenimports)} hidden imports")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "easyocr",
        "sentence_transformers",
        "transformers",
        "tokenizers",
        "safetensors",
        "torch",
        "torchvision",
        "cv2",
        "skimage",
        "scipy",
        "sklearn",
        "imageio",
        "matplotlib",
        "tkinter",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
        "sphinx",
        "PyQt5",
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
    name="AI Document Analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    uac_uiaccess=False,
    manifest="manifest.xml",
    icon="assets/logo.ico" if os.path.exists("assets/logo.ico") else None,
)
