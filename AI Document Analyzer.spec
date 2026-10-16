# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all


datas = [('assets', 'assets'), ('styles.qss', '.'), ('config.json', '.')]
easyocr_models_dir = os.path.join('models', 'easyocr')
if os.path.isdir(easyocr_models_dir) and os.listdir(easyocr_models_dir):
    datas.append((easyocr_models_dir, os.path.join('models', 'easyocr')))

binaries = []
hiddenimports = [
    'google.genai',
    'google.genai.types',
    'qdrant_client.local',
    'portalocker',
    'keyring',
    'keyring.backends',
]

for package in (
    'langchain_text_splitters',
    'langchain_core',
    'qdrant_client',
    'torch',
    'scipy',
    'sklearn',
    'easyocr',
    'google.generativeai',
    'google.genai',
    'keyring',
):
    tmp_ret = collect_all(package)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AI Document Analyzer',
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
    icon=['assets\\logo.ico'],
)
