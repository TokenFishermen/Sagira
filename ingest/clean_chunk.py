"""clean_chunk.py
Simple markdown/text cleaning utilities used by ingestion.
"""
import re

def clean_markdown(md_text: str) -> str:
    """Strip markdown, code fences, and reduce whitespace."""
    if not md_text:
        return ""
    # Remove code fences
    text = re.sub(r"```[\s\S]*?```", " ", md_text)
    # Remove inline code
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Remove markdown links but keep the text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove headings
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{2,}", "\n\n", text)
    # Strip excessive whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
