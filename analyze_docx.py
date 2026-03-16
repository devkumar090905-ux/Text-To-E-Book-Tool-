import docx
import json

def analyze_docx(file_path):
    doc = docx.Document(file_path)
    data = []
    for para in doc.paragraphs:
        if para.text.strip():
            style = para.style.name
            # Check for bold in runs
            runs = []
            for run in para.runs:
                if run.text.strip():
                    runs.append({
                        "text": run.text,
                        "bold": run.bold,
                        "italic": run.italic,
                        "font_size": run.font.size.pt if run.font.size else None
                    })
            data.append({
                "text": para.text,
                "style": style,
                "runs": runs
            })
            
    with open("docx_analysis.json", "w", encoding="utf-8") as f:
        json.dump(data[:50], f, ensure_ascii=False, indent=2) # First 50 paragraphs

if __name__ == "__main__":
    analyze_docx("1st Case Study Chapter 5 (1).docx")
