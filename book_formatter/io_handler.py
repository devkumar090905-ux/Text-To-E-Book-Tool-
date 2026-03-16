import os
from markdown import markdown

class IOHandler:
    @staticmethod
    def read_markdown(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def read_docx(file_path):
        try:
            import docx
        except ImportError:
            print("Warning: python-docx not installed. Run 'pip install python-docx'.")
            return []
            
        doc = docx.Document(file_path)
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                # 1. Merge runs with same formatting to avoid **** markers
                merged_runs = []
                if para.runs:
                    current_run = {"text": para.runs[0].text, "bold": para.runs[0].bold, "italic": para.runs[0].italic, "size": para.runs[0].font.size.pt if para.runs[0].font.size else 0}
                    for run in para.runs[1:]:
                        run_size = run.font.size.pt if run.font.size else 0
                        if run.bold == current_run["bold"] and run.italic == current_run["italic"]:
                            current_run["text"] += run.text
                        else:
                            merged_runs.append(current_run)
                            current_run = {"text": run.text, "bold": run.bold, "italic": run.italic, "size": run_size}
                    merged_runs.append(current_run)
                
                # 2. Build text with markers and find max font size
                text_with_markers = ""
                max_font_size = 0
                all_bold = True if merged_runs else False
                
                for run in merged_runs:
                    t = run["text"]
                    if not t.strip(): continue # Don't let spaces break 'all_bold' check
                    
                    if run["size"] > max_font_size:
                        max_font_size = run["size"]
                    
                    if not run["bold"]:
                        all_bold = False
                    
                    styled_t = t
                    if run["bold"]: styled_t = f"**{styled_t}**"
                    if run["italic"]: styled_t = f"*{styled_t}*"
                    text_with_markers += styled_t
                
                style_name = (para.style.name or "normal").lower().strip()
                detected_style = "normal"
                
                # 3. Enhanced Heading Detection
                # A. Style name check
                if "heading 1" in style_name or style_name == "h1":
                    detected_style = "heading 1"
                elif "heading 2" in style_name or style_name == "h2":
                    detected_style = "heading 2"
                elif "heading" in style_name:
                    detected_style = "heading 2"
                
                # B. Keyword check (Hindi)
                text_clean = para.text.strip()
                keywords_h1 = ["अध्याय", "विषय-सूची"]
                keywords_h2 = ["निष्कर्ष", "सारांश", "भूमिका", "परिचय", "धन्यवाद"]
                
                if any(text_clean.startswith(k) for k in keywords_h1):
                    detected_style = "heading 1"
                elif any(text_clean.startswith(k) for k in keywords_h2):
                    detected_style = "heading 2"
                
                # C. Heuristics (Size or Full Bold)
                if detected_style == "normal":
                    if max_font_size > 18:
                        detected_style = "heading 1"
                    elif max_font_size > 15 or (all_bold and len(text_clean) < 100):
                        detected_style = "heading 2"

                content.append({
                    "text": text_with_markers,
                    "raw_text": para.text,
                    "style": detected_style
                })
        return content

    @staticmethod
    def save_pdf(pdf, output_path):
        pdf.output(output_path)
        print(f"Book saved successfully to: {output_path}")
