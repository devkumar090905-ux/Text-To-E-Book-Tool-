from fpdf import FPDF
from .styler import BookStyle
import re

class FormatterEngine:
    def __init__(self, style: BookStyle):
        self.style = style
        # Initialize PDF with custom book format (e.g. 6x9 inches in mm)
        self._init_pdf()
        self.chapters = []

    def _init_pdf(self):
        # Always enable text_shaping=True for Hindi/Complex scripts
        # Use style.page_format provided in styler (152.4x228.6 mm for 6x9)
        self.pdf = FPDF(orientation='P', unit='mm', format=self.style.page_format)
        self.pdf.set_text_shaping(True)
        
        # Register fonts
        self.pdf.add_font(self.style.font_name, '', self.style.font_path)
        self.pdf.add_font(self.style.font_name, 'B', self.style.bold_font_path)
        
        # Set margins BEFORE add_page
        self.pdf.set_margins(self.style.margin_left, self.style.margin_top, self.style.margin_right)
        self.pdf.set_auto_page_break(auto=True, margin=self.style.margin_bottom)
        
        # Start with one page
        self.pdf.add_page()
        self._apply_body_style()

    def _apply_body_style(self):
        self.pdf.set_font(self.style.font_name, '', self.style.body_font_size)

    def _apply_h1_style(self):
        self.pdf.set_font(self.style.font_name, 'B', self.style.h1_font_size)

    def _apply_h2_style(self):
        self.pdf.set_font(self.style.font_name, 'B', self.style.h2_font_size)

    def _write_styled_line(self, line, height, align):
        # Calculate available width explicitly
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        if eff_w <= 10: eff_w = 10 
        
        # Enable markdown=True for bold/italic support (**bold**, *italic*)
        # fpdf2's markdown mode handles these markers
        try:
            # Note: We use the raw line which contains markers like ** text **
            self.pdf.multi_cell(eff_w, height, line, align=align, markdown=True)
            self.pdf.ln(height / 2)
        except Exception as e:
            # Fallback if markdown rendering fails for specific line
            print(f"DEBUG: Markdown render failed for line: {line[:30]}... Error: {e}")
            clean_line = line.replace('**', '').replace('*', '')
            self.pdf.multi_cell(eff_w, height, clean_line, align=align)
            self.pdf.ln(height / 2)

    def add_chapter_title(self, title):
        # Chapters ALWAYS start on a new page unless we are already on an empty first page
        if self.pdf.page_no() > 1 or self.pdf.y > self.pdf.t_margin + 10:
            self.pdf.add_page()
        
        self.chapters.append((title, 1, self.pdf.page_no()))
        self._apply_h1_style()
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        # Center title and add significant space
        self.pdf.ln(20)
        self.pdf.multi_cell(eff_w, 15, title, align='C')
        self.pdf.ln(15)
        self._apply_body_style()

    def add_section_title(self, title):
        # Avoid stranding a section title at the bottom of a page
        if self.pdf.y > self.pdf.h - 40:
            self.pdf.add_page()
            
        self.chapters.append((title, 2, self.pdf.page_no()))
        self._apply_h2_style()
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        self.pdf.ln(5)
        self.pdf.multi_cell(eff_w, 12, title, align='L')
        self.pdf.ln(5)
        self._apply_body_style()

    def generate_full_book(self, content_list, output_path):
        """Single-pass robust generation with professional styles."""
        print(f"DEBUG: Generating premium book. Items: {len(content_list)}")
        
        for i, item in enumerate(content_list):
            try:
                style = item.get('style', 'normal').lower()
                # Use 'text' which contains the bold/italic markers from IOHandler
                text = item.get('text', '')
                
                if not text.strip(): continue

                if 'heading 1' in style:
                    # Strip markers from chapter titles for clean look
                    clean_title = text.replace('**', '').replace('*', '')
                    self.add_chapter_title(clean_title)
                elif 'heading 2' in style:
                    clean_section = text.replace('**', '').replace('*', '')
                    self.add_section_title(clean_section)
                else:
                    self._apply_body_style()
                    self._write_styled_line(text, self.style.body_line_height, self.style.body_align)
            except Exception as e:
                print(f"CRITICAL ERROR at item {i}: {e}")
                raise e

        # Final output
        self.pdf.output(output_path)
        print(f"PREMIUM PDF GENERATED: {output_path}")

    def add_page_numbers(self):
        def footer():
            self.pdf.set_y(-15)
            self.pdf.set_font(self.style.font_name, '', 10)
            self.pdf.cell(0, 10, f"- {self.pdf.page_no()} -", align='C')
        self.pdf.footer = footer

    def add_text(self, text):
        """Standard markdown processing if needed."""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                self.pdf.ln(self.style.body_line_height / 2)
                continue
            
            if line.startswith('# '):
                self.add_chapter_title(line[2:])
            elif line.startswith('## '):
                self.add_section_title(line[3:])
            else:
                self._apply_body_style()
                self._write_styled_line(line, self.style.body_line_height, self.style.body_align)

    def get_pdf(self):
        return self.pdf
