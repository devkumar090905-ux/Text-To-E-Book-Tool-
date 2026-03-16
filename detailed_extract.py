from pypdf import PdfReader
import json

def extract_detailed_info(pdf_path):
    reader = PdfReader(pdf_path)
    info = {
        "metadata": dict(reader.metadata),
        "pages": []
    }
    
    # Check fonts
    fonts = set()
    for page in reader.pages:
        if "/Resources" in page and "/Font" in page["/Resources"]:
            f_dict = page["/Resources"]["/Font"]
            for f in f_dict:
                fonts.add(f_dict[f].get("/BaseFont", "Unknown"))
    info["fonts"] = list(fonts)

    for i in range(min(5, len(reader.pages))):
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
            "width": float(page.mediabox.width),
            "height": float(page.mediabox.height),
            "elements": text_data
        })
        
    with open("pdf_analysis.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_detailed_info("reference.pdf")
