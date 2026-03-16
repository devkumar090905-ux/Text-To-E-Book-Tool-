from pypdf import PdfReader
import sys

def deep_analyze(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"Total Pages: {len(reader.pages)}")
        
        # Analyze first 10 pages for structure
        for i in range(min(10, len(reader.pages))):
            page = reader.pages[i]
            mb = page.mediabox
            w, h = float(mb.width), float(mb.height)
            
            print(f"\n--- Page {i+1} ({w:.2f}pt x {h:.2f}pt) ---")
            
            # Try to get text with positions
            text_instances = []
            def visitor_body(text, cm, tm, font_dict, font_size):
                if text.strip():
                    text_instances.append({
                        "text": text.strip(),
                        "x": tm[4],
                        "y": tm[5],
                        "size": font_size
                    })
            
            page.extract_text(visitor_text=visitor_body)
            
            if not text_instances:
                print("No text found (might be an image-only page)")
                continue
                
            # Filter some samples
            # Sort by Y descending (top to bottom)
            text_instances.sort(key=lambda x: x['y'], reverse=True)
            
            # Print top 3 and bottom 3 elements to identify headers/footers
            print("Top elements:")
            for inst in text_instances[:5]:
                print(f"  Pos({inst['x']:.1f}, {inst['y']:.1f}) Size({inst['size']:.1f}): {inst['text'][:50]}")
                
            print("Bottom elements:")
            for inst in text_instances[-5:]:
                print(f"  Pos({inst['x']:.1f}, {inst['y']:.1f}) Size({inst['size']:.1f}): {inst['text'][:50]}")
                
            # Estimate margins
            xs = [inst['x'] for inst in text_instances]
            ys = [inst['y'] for inst in text_instances]
            print(f"Content Bounds: X({min(xs):.1f} to {max(xs):.1f}), Y({min(ys):.1f} to {max(ys):.1f})")
            print(f"Estimated Margins: Left({min(xs):.1f}), Right({w - max(xs):.1f}), Top({h - max(ys):.1f}), Bottom({min(ys):.1f})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf_file = "reference.pdf"
    deep_analyze(pdf_file)
