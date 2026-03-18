import docx
import os

def analyze_docx(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    doc = docx.Document(file_path)
    print(f"Analyzing: {file_path}")
    print("-" * 50)
    
    # Print first 20 paragraphs with their styles
    for i, para in enumerate(doc.paragraphs[:50]):
        text = para.text.strip()
        if text:
            style = para.style.name
            # Check font size of first run if available
            size = para.runs[0].font.size.pt if para.runs and para.runs[0].font.size else "Unknown"
            bold = para.runs[0].bold if para.runs else "Unknown"
            print(f"P{i} [{style}] (Size: {size}, Bold: {bold}): {text[:100]}...")

if __name__ == "__main__":
    analyze_docx(r"d:\Projects\Office Work\Automate Formeting\📘 उड़ने की इजाज़त मत माँगो.docx")
