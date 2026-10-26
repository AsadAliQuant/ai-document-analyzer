---
name: offline-features-removal
description: Preferences for migrating offline AI features to online/free alternatives
metadata:
  type: project
---

> **Historical preference record.** The alternatives below predate the accepted Milestone 1 implementation and are not current architecture guidance. The application now uses Gemini Embedding 2 for embeddings, Gemini for all AI operations, and local Qdrant only for persistence/RAG. See `README_Windows_Deployment.md`, `LARGE_DOC_GUIDE.md`, and `CLAUDE.md`.

- can use gemini-embedding-2 OR nvidia/nemotron-3-embed-1b:free OR cloudflare workers neurons for embedding model, in the place of local embedding model for 100% free
- can use gemini vision models (gemini-3.1 already suports it) for OCR
- keep using Qdrant locally (little impact on loading speed and installer disk space)

**Why:** To reduce dependency on local offline models while keeping costs free and functionality high.
**How to apply:** When planning or refactoring document processing, prioritize these alternatives over bundled local models.
