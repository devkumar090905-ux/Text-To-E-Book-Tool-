from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid
from book_formatter.io_handler import IOHandler
from book_formatter.styler import BookStyle
from book_formatter.engine import FormatterEngine

app = FastAPI(title="Book Formatter API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "temp_outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/format")
async def format_book(
    file: UploadFile = File(...),
    font_size: int = Form(12),
    font_name: str = Form("Inter"),
    margin: int = Form(25),
    line_spacing: float = Form(1.5)
):
    # 1. Save uploaded file
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    output_path = os.path.join(OUTPUT_DIR, f"formatted_{file_id}.pdf")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Process content
        if input_path.lower().endswith('.docx'):
            content = IOHandler.read_docx(input_path)
            is_structured = True
        else:
            content = IOHandler.read_markdown(input_path)
            is_structured = False

        # 3. Initialize style with user parameters
        style = BookStyle()
        style.body_font_size = font_size
        style.margin_left = margin
        style.margin_right = margin
        style.margin_top = margin
        style.margin_bottom = margin

        engine = FormatterEngine(style)
        engine.add_page_numbers()

        # 4. Generate PDF
        if is_structured:
            engine.generate_full_book(content, output_path)
        else:
            engine.add_text(content)
            IOHandler.save_pdf(engine.get_pdf(), output_path)

        # 5. Return PDF
        if os.path.exists(output_path):
            return FileResponse(
                output_path, 
                media_type="application/pdf", 
                filename=f"formatted_{file.filename.split('.')[0]}.pdf"
            )
        else:
            raise HTTPException(status_code=500, detail="PDF generation failed")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        # Cleanup input file (optional, maybe keep for a while)
        if os.path.exists(input_path):
            os.remove(input_path)

@app.get("/")
async def root():
    return {"message": "Book Formatter API is running"}

if __name__ == "__main__":
    import uvicorn
    # Using reload=False because we are running in a script, but we'll restart manually
    uvicorn.run(app, host="0.0.0.0", port=8000)
