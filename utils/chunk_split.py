import re
from typing import List, Literal, Tuple

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

def extract_title_and_description(text: str) -> Tuple[str, str, str]:
    lines = text.splitlines()
    title = ""
    start_idx = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            title = ln.strip()
            start_idx = i + 1
            break
    desc_lines = []
    body_start = start_idx
    for j, ln in enumerate(lines[start_idx:], start=start_idx):
        if re.match(r'^(第[一二三四五六七八九十百千万]+[章条])', ln):
            body_start = j
            break
        if ln.strip():
            desc_lines.append(ln.strip())
    description = "\n".join(desc_lines).strip()
    body = "\n".join(lines[body_start:]).strip()
    return title, description, body

# def semantic_split(
#     text: str,
#     mode: Literal['section', 'chunk', 'legal_section', 'legal_chunk'] = 'section',
#     min_section_size: int = 300,
#     min_chunk_size: int = 100,
#     max_chunk_size: int = 500
# ) -> List[str]:
#     def split_section(txt: str) -> List[str]:
#         if '\n\n' in txt or '\r\n\r\n' in txt:
#             parts = re.split(r'\r\n\r\n|\n\n', txt)
#         else:
#             parts = re.split(r'\r\n|\n|\r', txt)
#         blocks = [p.strip() for p in parts if p.strip()]
#         return merge_small(blocks, min_section_size, "\n\n")

#     def split_chunk(block: str) -> List[str]:
#         if len(block) < max_chunk_size:
#             return [block]
#         paras = re.split(r'(?:\r\n|\n){2,}', block)
#         chunks = []
#         for p in paras:
#             p = p.strip()
#             if not p:
#                 continue
#             if len(p) <= max_chunk_size:
#                 chunks.append(p)
#             else:
#                 sents = re.split(r'(?<=[。！？!?])\s*', p)
#                 buf = []
#                 total = 0
#                 for s in sents:
#                     if total + len(s) <= max_chunk_size:
#                         buf.append(s)
#                         total += len(s)
#                     else:
#                         if buf:
#                             chunks.append(''.join(buf))
#                         buf = [s]
#                         total = len(s)
#                 if buf:
#                     chunks.append(''.join(buf))
#         return merge_small(chunks, min_chunk_size)

#     def split_legal_section(text: str) -> List[str]:
#         lines = text.splitlines()
#         sections: List[str] = []
#         curr_para: List[str] = []
#         for ln in lines:
#             if not ln.strip():
#                 continue
#             if re.match(r'^\S', ln):
#                 if curr_para:
#                     sections.append("\n".join(curr_para))
#                 curr_para = [ln]
#             else:
#                 curr_para.append(ln)
#         if curr_para:
#             sections.append("\n".join(curr_para))
#         return sections
    
#     def split_legal_chunk(block: str) -> List[str]:
#         pattern = r'(?m)(?=^[\u3000 \t]*第[一二三四五六七八九十百千万]+条)'
#         raw_chunks = re.split(pattern, block)
#         temp = [
#             chunk.lstrip()
#             for chunk in raw_chunks
#             if chunk.strip()
#         ]
#         title = temp.pop(0).rstrip('\n')
#         chunks = []
#         for chunk in temp:
#             c = title + "." + chunk.strip()
#             chunks.append(c)
#         return chunks

#     if mode == 'section':
#         return split_section(text)
#     elif mode == 'chunk':
#         return split_chunk(text)
#     elif mode == 'legal_section':
#         return split_legal_section(text)
#     elif mode == 'legal_chunk':
#         return split_legal_chunk(text)

def semantic_split(text: str, max_chunk_size: int = 500) -> list[str]:
    """
    将原文按语义分割为不超过 max_chunk_size 的多个片段。
    优先使用段落、句号、标点等进行切分。
    若句子本身超长，也进行强制切分。
    """
    if not text:
        return []

    # 粗略按段落拆分
    paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]

    chunks = []
    for para in paragraphs:
        buffer = ""
        sentences = re.split(r'(?<=[。！？.!?；;])', para)
        for sent in sentences:
            sent = sent.strip()
            # 强制切分过长句子
            while len(sent) > max_chunk_size:
                part = sent[:max_chunk_size]
                if buffer:
                    chunks.append(buffer.strip())
                    buffer = ""
                chunks.append(part.strip())
                sent = sent[max_chunk_size:]
            if len(buffer) + len(sent) <= max_chunk_size:
                buffer += sent
            else:
                if buffer:
                    chunks.append(buffer.strip())
                buffer = sent
        if buffer:
            chunks.append(buffer.strip())
    return chunks