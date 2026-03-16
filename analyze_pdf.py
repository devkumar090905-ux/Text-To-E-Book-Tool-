from pypdf import PdfReader
import sys

def analyze(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        mb = page.mediabox
        width_pt = mb.width
        height_pt = mb.height
        
        # Convert pts to mm (1 pt = 1/72 inch, 1 inch = 25.4 mm)
        width_mm = float(width_pt) * 25.4 / 72
        height_mm = float(height_pt) * 25.4 / 72
        
        print(f"Dimensions_PT: {width_pt}x{height_pt}")
        print(f"Dimensions_MM: {width_mm:.2f}x{height_mm:.2f}")
        
        # Check text sample
        text = page.extract_text()
        print(f"Text_Sample: {text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze("reference.pdf")
