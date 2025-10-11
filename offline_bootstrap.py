import json
import os
import sys
import time
import shutil
import socket
import argparse
from dataclasses import dataclass
from typing import Callable, Dict, Optional


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
    os.path.join("sentence_transformers", "all-MiniLM-L6-v2"),
    os.path.join("models--sentence-transformers--all-MiniLM-L6-v2"),
    os.path.join("sentence-transformers_all-MiniLM-L6-v2"),
    # EasyOCR model folder (we assume a subfolder named 'easyocr' contains all weights)
    os.path.join("easyocr"),
]


@dataclass(frozen=True)
class OfflineAssetTask:
    name: str
    title: str
    check: Callable[[str], bool]
    prepare: Callable[[str], bool]


DEFAULT_STATE: Dict[str, object] = {
    "offline_ready": False,
    "tasks": {},
    "last_updated": 0,
}


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


def _has_sentence_transformer_cache(target_models_dir: str) -> bool:
    def _contains_model_files(path: str) -> bool:
        try:
            for root, _dirs, files in os.walk(path):
                for name in files:
                    lowered = name.lower()
                    if lowered.endswith((".bin", ".safetensors", ".pt")):
                        return True
                    if lowered in {"config.json", "tokenizer.json", "modules.json"}:
                        return True
        except Exception:
            return False
        return False

    candidates = [
        os.path.join(target_models_dir, "sentence-transformers", "all-MiniLM-L6-v2"),
        os.path.join(target_models_dir, "sentence_transformers", "all-MiniLM-L6-v2"),
        os.path.join(target_models_dir, "sentence-transformers_all-MiniLM-L6-v2"),
        os.path.join(target_models_dir, "all-MiniLM-L6-v2"),
    ]

    for path in candidates:
        if os.path.isdir(path) and _contains_model_files(path):
            return True

    # HuggingFace Hub style cache directories (models--<org>--<model>)
    try:
        for entry in os.listdir(target_models_dir):
            if "all-MiniLM-L6-v2" not in entry:
                continue
            path = os.path.join(target_models_dir, entry)
            if os.path.isdir(path) and _contains_model_files(path):
                return True
    except Exception:
        pass

    return False


def _ensure_sentence_transformer_cached(target_models_dir: str) -> bool:
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=target_models_dir,
        )
        return _has_sentence_transformer_cache(target_models_dir)
    except Exception as exc:
        print(f"[offline_bootstrap] SentenceTransformer preload failed: {exc}")
        import traceback
        traceback.print_exc()
        # Best-effort; skip if offline or any error
        return _has_sentence_transformer_cache(target_models_dir)


def _has_easyocr_cache(target_models_dir: str) -> bool:
    easy_dir = os.path.join(target_models_dir, "easyocr")
    if not os.path.isdir(easy_dir):
        return False
    try:
        for entry in os.listdir(easy_dir):
            if entry.endswith(".pth") or entry.endswith(".bin"):
                return True
    except Exception:
        return False
    for root, _dirs, files in os.walk(easy_dir):
        if any(name.endswith(".pth") or name.endswith(".bin") for name in files):
            return True
    return False


def _ensure_easyocr_models_cached(target_models_dir: str) -> bool:
    try:
        import easyocr  # type: ignore
        # Trigger model download into our target directory
        easyocr.Reader(
            ["en", "ar"],
            gpu=False,
            model_storage_directory=os.path.join(target_models_dir, "easyocr"),
            download_enabled=True,
        )
        return _has_easyocr_cache(target_models_dir)
    except Exception:
        # Best-effort; skip if offline or any error
        return _has_easyocr_cache(target_models_dir)


def _load_state(path: Optional[str]) -> Dict[str, object]:
    if not path:
        return dict(DEFAULT_STATE)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return dict(DEFAULT_STATE)
        merged = dict(DEFAULT_STATE)
        merged.update(data)
        if "tasks" not in merged or not isinstance(merged["tasks"], dict):
            merged["tasks"] = {}
        return merged
    except Exception:
        return dict(DEFAULT_STATE)


def _save_state(path: Optional[str], state: Dict[str, object]) -> None:
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
    except Exception:
        pass


def _build_tasks() -> tuple[OfflineAssetTask, ...]:
    return (
        OfflineAssetTask(
            name="embeddings",
            title="Embedding model",
            check=_has_sentence_transformer_cache,
            prepare=_ensure_sentence_transformer_cached,
        ),
        OfflineAssetTask(
            name="easyocr",
            title="EasyOCR weights",
            check=_has_easyocr_cache,
            prepare=_ensure_easyocr_models_cached,
        ),
    )


def prepare_offline_assets(
    target_models_dir: str,
    state_path: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Dict[str, object]:
    """Prepare local caches for embeddings and OCR.

    Strategy:
    1) If a bundled 'models/' folder exists next to the app, copy its contents
       into the appdata models dir.
    2) If internet is available, prefetch the SentenceTransformer and EasyOCR weights
       into the appdata models dir (best-effort, on background thread).
    """
    state = _load_state(state_path)
    tasks = _build_tasks()
    total_tasks = len(tasks)
    ready_count = 0
    last_message = "Preparing offline assets..."

    def emit(progress: float, message: str) -> None:
        nonlocal last_message
        if message:
            last_message = message
        if progress_callback is None:
            return
        try:
            bounded = max(0.0, min(100.0, progress))
            progress_callback(bounded, message)
        except Exception:
            pass

    emit(0.0, last_message)

    try:
        os.makedirs(target_models_dir, exist_ok=True)
    except Exception:
        emit(0.0, "Offline assets unavailable")
        state.update(
            {
                "offline_ready": False,
                "tasks": {task.name: False for task in tasks},
                "last_updated": int(time.time()),
                "progress": 0.0,
                "message": last_message,
            }
        )
        _save_state(state_path, state)
        return state

    bundle_dir = _app_bundle_dir()
    bundled_models_dir = os.path.join(bundle_dir, "models")

    # Step 1: Copy pre-bundled models if present
    if os.path.isdir(bundled_models_dir):
        for sub in essential_model_subdirs:
            src = os.path.join(bundled_models_dir, sub)
            dst = os.path.join(target_models_dir, sub)
            _copy_tree(src, dst)

    if total_tasks == 0:
        emit(100.0, "READY for Offline use")
        state.update({
            "offline_ready": True,
            "tasks": {},
            "last_updated": int(time.time()),
            "progress": 100.0,
            "message": last_message,
        })
        _save_state(state_path, state)
        return state

    results: Dict[str, bool] = {}
    emit(0.0, "Checking offline assets...")

    for task in tasks:
        emit((ready_count / total_tasks) * 100.0, f"Checking {task.title}...")
        already_present = False
        try:
            already_present = task.check(target_models_dir)
        except Exception:
            already_present = False

        if already_present:
            results[task.name] = True
            ready_count = sum(1 for value in results.values() if value)
            emit((ready_count / total_tasks) * 100.0, f"{task.title} ready")
            continue

        if not _internet_available():
            results[task.name] = False
            emit((ready_count / total_tasks) * 100.0, f"{task.title} requires internet connection")
            continue

        emit((ready_count / total_tasks) * 100.0, f"Downloading {task.title}...")
        success = False
        try:
            success = task.prepare(target_models_dir)
        except Exception:
            success = False

        if not success:
            try:
                success = task.check(target_models_dir)
            except Exception:
                success = False

        results[task.name] = success
        if success:
            ready_count = sum(1 for value in results.values() if value)
            emit((ready_count / total_tasks) * 100.0, f"{task.title} ready")
        else:
            emit((ready_count / total_tasks) * 100.0, f"{task.title} download failed")

    ready_count = sum(1 for value in results.values() if value)
    offline_ready = (ready_count == total_tasks and total_tasks > 0)
    final_progress = 100.0 if offline_ready else (ready_count / total_tasks) * 100.0
    emit(final_progress, "READY for Offline use" if offline_ready else last_message)

    state.update(
        {
            "offline_ready": offline_ready,
            "tasks": results,
            "last_updated": int(time.time()),
            "progress": final_progress,
            "message": last_message,
        }
    )
    _save_state(state_path, state)
    return state


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
