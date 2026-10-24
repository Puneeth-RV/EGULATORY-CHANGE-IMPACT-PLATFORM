"""Build text-based judge demo PDFs from the editable sample text files."""
from pathlib import Path
import fitz

root = Path(__file__).parents[1] / "sample_data"
for text_file in root.glob("*/*.txt"):
    pdf_file = text_file.with_suffix(".pdf")
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    box = fitz.Rect(54, 54, 541, 788)
    overflow = page.insert_textbox(box, text_file.read_text(), fontsize=11, fontname="helv", lineheight=1.45)
    if overflow < 0:
        raise ValueError(f"Text does not fit: {text_file}")
    document.save(pdf_file)
    document.close()
    print(pdf_file)
