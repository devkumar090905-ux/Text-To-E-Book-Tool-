from pypdf import PdfReader
import json

def extract_more(pdf_path):
    reader = PdfReader(pdf_path)
    info = {"pages": []}
    for i in range(5, min(15, len(reader.pages))):
        page = reader.pages[i]
        text_data = []
        def visitor(text, cm, tm, font_dict, font_size):
            if text.strip():
                text_data.append({
                    "t": text.strip(),
                    "x": round(tm[4], 1),
                    "y": round(tm[5], 1),
                    "s": round(font_size, 1)
                })
        page.extract_text(visitor_text=visitor)
        info["pages"].append({
            "number": i+1,
            "elements": text_data
        })
        
    with open("pdf_analysis_ext.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_more("reference.pdf")
