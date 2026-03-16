class BookStyle:
    def __init__(self):
        # Precise Page settings for 432x648 pts
        self.page_format = (152.4, 228.6)
        self.unit = 'mm'
        
        # Margins (Derived from analysis)
        self.margin_left = 18
        self.margin_right = 18
        self.margin_top = 22
        self.margin_bottom = 18
        
        # Fonts (Nirmala UI is good for Hindi)
        self.font_name = 'HindiFont'
        self.font_path = r'C:\Windows\Fonts\Nirmala.ttf'
        self.bold_font_path = r'C:\Windows\Fonts\NirmalaB.ttf'
        
        # Body text
        self.body_font_size = 12
        self.body_line_height = 9
        
        # Headings (Reduced sizes as per user request)
        self.h1_font_size = 20
        self.h1_bold = True
        
        self.h2_font_size = 16
        self.h2_bold = True
        
        # Alignment
        self.body_align = 'J'  # Justified
        
        # Meta info
        self.website = "Vyaktigatvikas.com"
