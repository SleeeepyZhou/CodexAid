from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def semantic_split(text: str, max_chunk_size: int = 500) -> list[str]:
    """
    将原文按语义分割为不超过 max_chunk_size 的多个片段。
    """
    if not text:
        return []

    # 首先按标题进行初步切分
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
        ("######", "Header 6")
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(text)
    
    chunk_overlap = 30
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=max_chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(md_header_splits)

    chunks = []
    for split in splits:
        header = ""
        for i, h in enumerate(split.metadata.items()):
            header += "#"*(i+1) + h[1]
        chunk = header + "\n" + split.page_content
        chunks.append(chunk)

    return chunks

if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    with open(os.path.join(data_dir, "deeppath.md"), "r", encoding="utf-8") as f:
        text = f.read()

    chunks = semantic_split(text, max_chunk_size=500)
    print(f"Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\n\nChunk {i+1}: {chunk}")