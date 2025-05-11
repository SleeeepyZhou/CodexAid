import re
from typing import List, Literal

def merge_small(chunks: list[str], min_size: int = 100, insert: str = ""):
    merged = []
    buf = []
    for chunk in chunks:
        if len(chunk) < min_size:
            buf.append(chunk)
        else:
            if buf:
                merged.append(insert.join(buf))
                buf = []
            merged.append(chunk)
    if buf:
        merged.append(insert.join(buf))
    return merged

def semantic_split(
    text: str,
    mode: Literal['section', 'chunk'] = 'section',
    min_section_size: int = 300,
    min_chunk_size: int = 100,
    max_chunk_size: int = 500
) -> List[str]:
    def split_section(txt: str) -> List[str]:
        if '\n\n' in txt or '\r\n\r\n' in txt:
            parts = re.split(r'\r\n\r\n|\n\n', txt)
        else:
            parts = re.split(r'\r\n|\n|\r', txt)
        blocks = [p.strip() for p in parts if p.strip()]
        return merge_small(blocks, min_section_size, "\n\n")

    def split_chunk(block: str) -> List[str]:
        if len(block) < max_chunk_size:
            return [block]
        paras = re.split(r'(?:\r\n|\n){2,}', block)
        chunks = []
        for p in paras:
            p = p.strip()
            if not p:
                continue
            if len(p) <= max_chunk_size:
                chunks.append(p)
            else:
                sents = re.split(r'(?<=[。！？!?])\s*', p)
                buf = []
                total = 0
                for s in sents:
                    if total + len(s) <= max_chunk_size:
                        buf.append(s)
                        total += len(s)
                    else:
                        if buf:
                            chunks.append(''.join(buf))
                        buf = [s]
                        total = len(s)
                if buf:
                    chunks.append(''.join(buf))
        return merge_small(chunks, min_chunk_size)

    if mode == 'section':
        return split_section(text)
    elif mode == 'chunk':
        return split_chunk(text)