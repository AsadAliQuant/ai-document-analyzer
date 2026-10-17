# -*- mode: python ; coding: utf-8 -*-
"""Alternate PyInstaller single-file build definition."""

import os
from PyInstaller.utils.hooks import collect_all


datas = [("assets", "assets"), ("styles.qss", "."), ("config.json", ".")]
binaries = []
hiddenimports = [
    "google.genai",
    "google.genai.types",
    "gemini_fallback",
    "gemini_ocr",
    "qdrant_client.local",
    "portalocker",
    "keyring",
    "keyring.backends",
]

for package in (
    "langchain_text_splitters",
    "langchain_core",
    "qdrant_client",
    "google.genai",
    "keyring",
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports


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
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AI Document Analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["assets\\logo.ico"] if os.path.exists("assets/logo.ico") else None,
)
