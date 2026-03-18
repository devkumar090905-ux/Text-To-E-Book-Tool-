from fpdf import FPDF
from .styler import BookStyle
import re

class FormatterEngine:
    def __init__(self, style: BookStyle):
        self.style = style
        # Initialize PDF with custom book format (e.g. 6x9 inches in mm)
        self.pdf = None # Initialized in _init_pdf
        self.chapters = []
        self.toc_pages_count = 0
        self.page_no_offset = 0
        self._init_pdf()

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
        # Center title and add moderate space
        self.pdf.ln(10)
        self.pdf.multi_cell(eff_w, 12, title, align='C')
        self.pdf.ln(10)
        self._apply_body_style()

    def add_section_title(self, title):
        # Avoid stranding a section title at the bottom of a page
        if self.pdf.y > self.pdf.h - 40:
            self.pdf.add_page()
            
        self.chapters.append((title, 2, self.pdf.page_no()))
        self._apply_h2_style()
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        self.pdf.ln(5)
        self.pdf.multi_cell(eff_w, 10, title, align='L')
        self.pdf.ln(5)
        self._apply_body_style()

    def add_sub_section_title(self, title):
        # Level 3 headings
        if self.pdf.y > self.pdf.h - 30:
            self.pdf.add_page()
            
        self.chapters.append((title, 3, self.pdf.page_no()))
        self.pdf.set_font(self.style.font_name, 'B', self.style.h2_font_size - 3) # Smaller than H2
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        self.pdf.ln(3)
        self.pdf.multi_cell(eff_w, 7, title, align='L')
        self.pdf.ln(2)
        self._apply_body_style()

    def add_list_item_title(self, title):
        # Level 4 items (List bullets)
        if self.pdf.y > self.pdf.h - 20:
            self.pdf.add_page()
            
        self.chapters.append((title, 4, self.pdf.page_no()))
        self.pdf.set_font(self.style.font_name, '', self.style.body_font_size - 1)
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        # Don't add much space for list items in the main text, just write them
        self.pdf.multi_cell(eff_w, 6, f"• {title}", align='L')
        self.pdf.ln(1)
        self._apply_body_style()

    def generate_full_book(self, content_list):
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
                elif 'heading 3' in style:
                    clean_sub = text.replace('**', '').replace('*', '')
                    self.add_sub_section_title(clean_sub)
                elif 'heading 4' in style:
                    clean_list = text.replace('**', '').replace('*', '')
                    self.add_list_item_title(clean_list)
                else:
                    self._apply_body_style()
                    self._write_styled_line(text, self.style.body_line_height, self.style.body_align)
            except Exception as e:
                print(f"CRITICAL ERROR at item {i}: {e}")
                raise e


    def add_page_numbers(self):
        def footer():
            self.pdf.set_y(-15)
            self.pdf.set_font(self.style.font_name, '', 10)
            # Use current page_no plus our offset for display
            display_num = self.pdf.page_no() + self.page_no_offset
            self.pdf.cell(0, 10, f"- {display_num} -", align='C')
        self.pdf.footer = footer

    def add_toc(self):
        """Generates Index. If we are in 'index only' mode (or if preferred), 
        resets its display page numbers to start from 1."""
        if not self.chapters:
            return

        # 1. Reset page numbering for TOC pages so they start from 1
        # Current page_no() will be the last page of content.
        # The first TOC page will be page_no() + 1.
        # We want (page_no() + 1) + offset = 1  => offset = -page_no()
        self.page_no_offset = -self.pdf.page_no()

        # Record where TOC starts
        start_toc_page = self.pdf.page_no() + 1
        
        # Add a new page for Index
        self.pdf.add_page()
        style_font = self.style.font_name
        
        # Header "Contents" - Centered, Bold
        self.pdf.set_font(style_font, 'B', 24)
        eff_w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        
        self.pdf.ln(10)
        # Change title to "Contents" to match reference
        self.pdf.multi_cell(eff_w, 15, "Contents", align='C', ln=1)
        self.pdf.ln(10) # More space, no horizontal line as per reference

        # Print TOC items with bullets
        for title, level, page_number in self.chapters:
            clean_title = str(title).replace('**', '').replace('*', '').strip()
            if not clean_title: continue

            if level == 1:
                # Chapter level: Bold, Left-aligned, no bullet
                self.pdf.set_font(style_font, 'B', 11) # Reduced further
                self.pdf.ln(3)
                self.pdf.multi_cell(eff_w, 5, clean_title)
                self.pdf.ln(1)
            elif level == 2:
                # Section level
                self.pdf.set_font(style_font, 'B', 10) 
                self.pdf.set_x(self.pdf.l_margin + 4)
                self.pdf.cell(5, 4, "■ ")
                self.pdf.multi_cell(eff_w - 9, 4, clean_title, align='L')
            elif level == 3:
                # Subsection level (Level 3): Further indented, empty circle bullet
                self.pdf.set_font(style_font, '', 9)
                self.pdf.set_x(self.pdf.l_margin + 8)
                self.pdf.cell(5, 4, "◦ ")
                self.pdf.multi_cell(eff_w - 13, 4, clean_title, align='L')
            else:
                # Level 4 (Lists): Primary bullet points under chapters
                self.pdf.set_font(style_font, '', 9.5)
                self.pdf.set_x(self.pdf.l_margin + 4)
                self.pdf.cell(5, 4, "• ")
                self.pdf.multi_cell(eff_w - 9, 4, clean_title, align='L')


        # Record how many pages the TOC uses
        self.toc_pages_count = self.pdf.page_no() - start_toc_page + 1
        print(f"DEBUG: Index generated. Pages: {self.toc_pages_count}")
        # Note: We NO LONGER call move_page here because it's missing in some fpdf2 environments.
        # Instead, we will handle reordering in IOHandler using pypdf.

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
