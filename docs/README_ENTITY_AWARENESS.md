# Entity Awareness Middleware (added to Sagira)

This folder adds a minimal Entity Awareness pipeline to Sagira. It attempts to use spaCy, sentence-transformers and transformers when available but falls back to the project's `core.nlp_core` analyzer when heavy packages/models are not installed. This lets you test integration locally before installing large models.

Files added:

- `src/entity_awareness.py` - pipeline with safe fallbacks
- `src/memory.py` - in-memory conversation memory + KB index
- `src/prompting.py` - prompt builder to create persona-aware system prompts
- `examples/usage.py` - simple usage script demonstrating pipeline usage

How to enable in Sagira:

- Use the `--use-ea` CLI flag (main.py) to toggle usage of the entity-awareness adapter.

To enable full capability:

1. Add packages in the repository `requirements.txt` (spaCy, sentence-transformers, transformers).
2. Download the spaCy transformer model (e.g., `python -m spacy download en_core_web_trf` or install via wheel).
3. Install FAISS if you want faster KB search.

Run the example (fallback mode works without heavy models):

```bash
python examples/usage.py
```

Notes:

- In production, run spaCy and embedding models on dedicated workers if latency matters.
- Be careful with model sizes: `en_core_web_trf` and large transformer models can be >1GB.
