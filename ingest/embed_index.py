"""embed_index.py
Create a small KB index from text chunks using sentence-transformers (fallback safe).

Usage (example):
  python embed_index.py input.txt output_kb.json

If sentence-transformers is not installed, the script will create simple hashed vectors so you can still test retrieval behavior.
"""
import json
import sys
from ingest.clean_chunk import clean_markdown

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAVE_ST = True
except Exception:
    _HAVE_ST = False
    import hashlib

def chunk_text(text: str, chunk_size: int = 400) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(' '.join(words[i:i+chunk_size]))
    return chunks

def embed_chunks(chunks):
    if _HAVE_ST:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        vecs = model.encode(chunks, convert_to_numpy=True)
        return vecs.tolist()
    # fallback: simple hashed pseudo-vectors
    out = []
    for c in chunks:
        h = hashlib.sha256(c.encode('utf-8')).digest()
        # create small vector by interpreting bytes
        vec = [b/255.0 for b in h[:32]]
        out.append(vec)
    return out

def build_kb_from_text(text: str, title: str = 'doc'):
    clean = clean_markdown(text)
    chunks = chunk_text(clean, 200)
    embeddings = embed_chunks(chunks)
    items = []
    for i, (ch, emb) in enumerate(zip(chunks, embeddings)):
        items.append({
            'id': f"{title}-{i}",
            'title': title,
            'text': ch,
            'embedding': emb
        })
    return items

def save_kb(items, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python embed_index.py <input_file> <output_kb.json>')
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2]
    with open(inp, 'r', encoding='utf-8') as f:
        text = f.read()
    items = build_kb_from_text(text, title=inp.replace('.','_'))
    save_kb(items, out)
    print(f'Wrote {len(items)} chunks to {out}')
