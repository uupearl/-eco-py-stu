##word_to_txt.py


from pathlib import Path
from docx import Document

folder = Path("/Users/ww/Desktop/pre")

# 新建 txt 文件夹
txt_folder = folder / "txt"
txt_folder.mkdir(exist_ok=True)

# 批量处理所有 docx
for docx_file in folder.glob("*.docx"):

    doc = Document(docx_file)

    text = "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    )

    txt_file = txt_folder / f"{docx_file.stem}.txt"

    txt_file.write_text(text, encoding="utf-8")

    print(f"完成：{docx_file.name} → {txt_file.name}")

print("\n全部转换完成！")


