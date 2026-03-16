from book_formatter.io_handler import IOHandler
from book_formatter.styler import BookStyle
from book_formatter.engine import FormatterEngine
import sys
import os

import argparse

def main():
    parser = argparse.ArgumentParser(description="Professional Book Formatting Tool")
    parser.add_argument("-i", "--input", default="input_book.md", help="Path to input markdown file")
    parser.add_argument("-o", "--output", default="formatted_book.pdf", help="Path to output PDF file")
    
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Starting book formatting for: {input_file}")
    
    # Load content
    if input_file.lower().endswith('.docx'):
        content = IOHandler.read_docx(input_file)
        is_structured = True
    else:
        content = IOHandler.read_markdown(input_file)
        is_structured = False
    
    # Initialize style and engine
    style = BookStyle()
    engine = FormatterEngine(style)
    
    # Enable features
    engine.add_page_numbers()
    
    # Add content and generate
    if is_structured:
        engine.generate_full_book(content, output_file)
    else:
        # For markdown, we'll just use the old method for now or convert it
        engine.add_text(content)
        engine.add_toc()
        IOHandler.save_pdf(engine.get_pdf(), output_file)

if __name__ == "__main__":
    main()
