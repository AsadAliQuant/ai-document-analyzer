# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller one-folder build for AI Document Analyzer."""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules


block_cipher = None
datas = []
binaries = []
hiddenimports = []

for package in [
    "langchain_core",
    "langchain_text_splitters",
    "qdrant_client",
    "PyPDF2",
    "docx",
    "google.genai",
    "keyring",
    "cryptography",
]:
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
    "grpc._cython",
    "google.protobuf",
    "google.auth",
]:
    try:
        hiddenimports += collect_submodules(submodule)
    except Exception:
        hiddenimports.append(submodule)

hiddenimports += [
    "langchain_text_splitters",
    "langchain_text_splitters.character",
    "google.genai",
    "google.genai.types",
    "numpy",
    "qdrant_client",
    "qdrant_client.local",
    "sqlite3",
    "keyring",
    "keyring.backends",
    "keyring.backends.Windows",
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
    # These packages are optional imports of retained dependencies. Excluding
    # them prevents a developer's dirty venv from adding unused heavyweight
    # features to the release build.
    excludes=[
        "sentence_transformers",
        "transformers",
        "matplotlib",
        "IPython",
        "pytest",
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
    [],
    exclude_binaries=True,
    name="AI Document Analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AI Document Analyzer",
)
