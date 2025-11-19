"""
GLYPH ENGINE - Core Compression System
"""
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CompressionResult:
    original: str
    compressed: str
    tokens_before: int
    tokens_after: int
    compression_ratio: float
    cache_hit: bool
    glyph_ids: List[str]

class Grimoire:
    def __init__(self):
        self.glyphs = {}
        self.stats = {"hits": 0, "total": 0}
    
    def store(self, text_hash, original, compressed):
        self.glyphs[text_hash] = {
            "original": original,
            "compressed": compressed,
            "created": time.time(),
            "uses": 1
        }
    
    def get(self, text_hash):
        if text_hash in self.glyphs:
            self.glyphs[text_hash]["uses"] += 1
            return self.glyphs[text_hash]
        return None

class GlyphEngine:
    def __init__(self):
        self.grimoire = Grimoire()
        self.stats = {
            "total_compressions": 0,
            "cache_hits": 0,
            "tokens_saved": 0
        }
    
    def compress(self, text: str, learn: bool = True) -> CompressionResult:
        self.stats["total_compressions"] += 1
        
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        cached = self.grimoire.get(text_hash)
        
        if cached:
            self.stats["cache_hits"] += 1
            return CompressionResult(
                original=text,
                compressed=cached["compressed"],
                tokens_before=len(text.split()),
                tokens_after=len(cached["compressed"].split()),
                compression_ratio=0.7,
                cache_hit=True,
                glyph_ids=[text_hash]
            )
        
        # Compress: remove stopwords + abbreviate
        words = text.lower().split()
        stopwords = {"the", "a", "an", "is", "are", "was", "to", "of", "and", "in", "for", "on", "with", "this", "that"}
        filtered = [w for w in words if w not in stopwords]
        compressed = " ".join([w[:4] if len(w) > 4 else w for w in filtered[:12]])
        
        tokens_before = len(words)
        tokens_after = len(compressed.split())
        ratio = 1 - (tokens_after / max(1, tokens_before))
        
        # Store if learning
        if learn:
            self.grimoire.store(text_hash, text, compressed)
            self.stats["tokens_saved"] += tokens_before - tokens_after
        
        return CompressionResult(
            original=text,
            compressed=compressed,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            compression_ratio=ratio,
            cache_hit=False,
            glyph_ids=[text_hash]
        )
    
    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "grimoire_size": len(self.grimoire.glyphs),
            "hit_rate": f"{(self.stats['cache_hits']/max(1,self.stats['total_compressions']))*100:.1f}%"
        }
    
    def export_grimoire(self) -> Dict:
        return {
            "glyphs": self.grimoire.glyphs,
            "stats": self.stats,
            "exported_at": time.time()
        }
