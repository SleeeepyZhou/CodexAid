import mammoth
from markdownify import markdownify as md

def docx_to_md_semantic(input_path, output_path):
    # Step 1: DOCX -> HTML
    with open(input_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html = result.value
    # Step 2: HTML -> Markdown
    markdown = md(html, heading_style="ATX")
    # 保存到文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    from chunk_split import semantic_split
    import os
    word_folder = "E:/AI/Chat/Qwen3/data/word"
    md_folder = "E:/AI/Chat/Qwen3/data/markdown"
    for filename in os.listdir(word_folder):
        if filename.endswith(('.doc', '.docx')):
            word_path = os.path.join(word_folder, filename)
            md_filename = os.path.splitext(filename)[0] + '.md'
            md_path = os.path.join(md_folder, md_filename)
            docx_to_md_semantic(word_path, md_path)
            print(f'Converted {filename} to {md_filename}')