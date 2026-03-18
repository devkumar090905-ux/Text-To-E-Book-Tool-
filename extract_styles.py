import docx
import sys

def analyze_docx(file_path):
    try:
        doc = docx.Document(file_path)
        with open("docx_analysis_out.txt", "w", encoding="utf-8") as f:
            for i, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text: continue
                style = para.style.name
                size = "Unknown"
                bold = "Unknown"
                if para.runs:
                    if para.runs[0].font.size:
                        size = para.runs[0].font.size.pt
                    bold = para.runs[0].bold
                
                f.write(f"P{i} [{style}] (Size: {size}, Bold: {bold}): {text[:150]}\n")
                if i > 250: # just get enough to see a few chapters
                    break
        print("Done analyzing.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_docx(r"d:\Projects\Office Work\Automate Formeting\📘 उड़ने की इजाज़त मत माँगो.docx")
