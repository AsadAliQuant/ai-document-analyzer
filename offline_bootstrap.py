import os
import sys
import shutil
import socket
import argparse
from typing import Optional


def _app_bundle_dir() -> str:
    """Return the directory where bundled data (e.g., models/) resides.
    Works for both PyInstaller and normal runs.
    """
    # PyInstaller onefile sets _MEIPASS; onedir uses sys.executable dir
    if getattr(sys, "frozen", False):  # PyInstaller
        base = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return base


essential_model_subdirs = [
    # HuggingFace Sentence Transformers
    os.path.join("sentence-transformers", "all-MiniLM-L6-v2"),
    # EasyOCR model folder (we assume a subfolder named 'easyocr' contains all weights)
    os.path.join("easyocr"),
]


def _copy_tree(src: str, dst: str) -> None:
    if not os.path.exists(src):
        return
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target_root = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(target_root, exist_ok=True)
        for d in dirs:
            os.makedirs(os.path.join(target_root, d), exist_ok=True)
        for f in files:
            s = os.path.join(root, f)
            dpath = os.path.join(target_root, f)
            try:
                if os.path.islink(s):
                    # Resolve symlink to a regular file copy if possible
                    s = os.path.realpath(s)
                shutil.copy2(s, dpath)
            except Exception:
                # Best-effort copy; continue
                pass


def _internet_available(timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=timeout):
            return True
    except OSError:
        return False


def _ensure_sentence_transformer_cached(target_models_dir: str) -> None:
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=target_models_dir,
        )
    except Exception:
        # Best-effort; skip if offline or any error
        pass


def _ensure_easyocr_models_cached(target_models_dir: str) -> None:
    try:
        import easyocr  # type: ignore
        # Trigger model download into our target directory
        easyocr.Reader(
            ["en", "ar"],
            gpu=False,
            model_storage_directory=os.path.join(target_models_dir, "easyocr"),
            download_enabled=True,
        )
    except Exception:
        # Best-effort; skip if offline or any error
        pass


def prepare_offline_assets(target_models_dir: str) -> None:
    """Prepare local caches for embeddings and OCR.

    Strategy:
    1) If a bundled 'models/' folder exists next to the app, copy its contents
       into the appdata models dir.
    2) If internet is available, prefetch the SentenceTransformer and EasyOCR weights
       into the appdata models dir (best-effort, on background thread).
    """
    try:
        os.makedirs(target_models_dir, exist_ok=True)
    except Exception:
        return

    bundle_dir = _app_bundle_dir()
    bundled_models_dir = os.path.join(bundle_dir, "models")

    # Step 1: Copy pre-bundled models if present
    if os.path.isdir(bundled_models_dir):
        for sub in essential_model_subdirs:
            src = os.path.join(bundled_models_dir, sub)
            dst = os.path.join(target_models_dir, sub)
            _copy_tree(src, dst)

    # Step 2: Optional online prefetch (best-effort)
    if _internet_available():
        _ensure_sentence_transformer_cached(target_models_dir)
        _ensure_easyocr_models_cached(target_models_dir)


def _prefetch_into_repo_models(target_dir: str) -> None:
    os.makedirs(target_dir, exist_ok=True)
    # Download/copy directly into the repo models dir
    # Step 1: copy any existing bundled content from current working dir models (noop if same)
    src_models = os.path.join(os.getcwd(), "models")
    if os.path.isdir(src_models):
        _copy_tree(src_models, target_dir)
    # Step 2: fetch models if online
    if _internet_available():
        _ensure_sentence_transformer_cached(target_dir)
        _ensure_easyocr_models_cached(target_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline models bootstrap helper")
    parser.add_argument("--prefetch", action="store_true", help="Prefetch models into a target directory")
    parser.add_argument("--target", type=str, default="models", help="Target directory for models")
    args = parser.parse_args()
    if args.prefetch:
        try:
            _prefetch_into_repo_models(args.target)
            print(f"Prefetch completed into: {args.target}")
        except Exception as e:
            print(f"Prefetch error: {e}")
