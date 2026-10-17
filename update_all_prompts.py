"""Legacy prompt-update entry point.

The application now keeps image OCR instructions in ``gemini_ocr.py`` and text
summary/Q&A prompts in ``main_window.py``. Automatic source-code replacement was
retired because it referenced image-summary functions that no longer exist.
"""


if __name__ == "__main__":
    print(
        "No changes were made. Edit gemini_ocr.py for OCR transcription prompts "
        "or main_window.py for summary and Q&A prompts, then update "
        "PROMPTS_DOCUMENTATION.txt."
    )
