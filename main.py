import os
import io
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI(
    title="Chunks.ai Text Splitter API",
    description="A FastAPI application that splits raw text and PDF files into smaller chunks using LangChain's RecursiveCharacterTextSplitter.",
    version="1.0.0"
)

# Resolve templates path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Request schema for raw text split
class SplitRequest(BaseModel):
    text: str = Field(..., description="The raw text to split.")
    chunk_size: int = Field(default=50, description="The maximum size of each chunk. Must be > 0.")
    chunk_overlap: int = Field(default=10, description="The overlap size between chunks. Must be >= 0.")


def validate_params(chunk_size: int, chunk_overlap: int):
    """Helper method to validate chunking parameters."""
    if chunk_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="chunk_size must be a positive integer greater than 0."
        )
    if chunk_overlap < 0:
        raise HTTPException(
            status_code=400,
            detail="chunk_overlap must be a non-negative integer."
        )
    if chunk_overlap >= chunk_size:
        raise HTTPException(
            status_code=400,
            detail="chunk_overlap must be strictly less than chunk_size."
        )


@app.get("/", response_class=HTMLResponse)
async def welcome(request: Request):
    """
    Welcome endpoint (GET /).
    If accepted format is HTML (e.g. from browser), returns the interactive UI.
    Otherwise, returns a welcoming JSON response.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        try:
            return templates.TemplateResponse(request, "index.html")
        except TypeError:
            return templates.TemplateResponse("index.html", {"request": request})
    
    return JSONResponse(content={
        "message": "Welcome to the Chunks.ai Text Splitter API!",
        "docs_url": "/docs",
        "interactive_ui_url": "/",
        "usage": {
            "text_splitter": "POST /split (JSON payload: text, chunk_size, chunk_overlap)",
            "pdf_splitter": "POST /split-pdf (Multipart Form: file, chunk_size, chunk_overlap)"
        }
    })


@app.post("/split")
async def split_text_endpoint(payload: SplitRequest):
    """
    Splits input text into chunks using RecursiveCharacterTextSplitter.
    """
    # 1. Parameter Validation
    validate_params(payload.chunk_size, payload.chunk_overlap)
    
    # 2. Text Validation
    text_content = payload.text.strip()
    if not text_content:
        raise HTTPException(
            status_code=400,
            detail="Input text cannot be empty or whitespace-only."
        )

    # 3. Chunking logic
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
            length_function=len
        )
        chunks = splitter.split_text(text_content)
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while splitting the text: {str(e)}"
        )


@app.post("/split-pdf")
async def split_pdf_endpoint(
    file: UploadFile = File(..., description="The PDF file to upload and split."),
    chunk_size: int = Form(50, description="The maximum size of each chunk. Must be > 0."),
    chunk_overlap: int = Form(10, description="The overlap size between chunks. Must be >= 0.")
):
    """
    Extracts text from an uploaded PDF and splits it into chunks.
    """
    # 1. Parameter Validation
    validate_params(chunk_size, chunk_overlap)

    # 2. File Type Validation
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # 3. PDF Content extraction
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
        
        extracted_text = extracted_text.strip()
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract any readable text from the PDF. The PDF may be scanned or empty."
            )
            
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error parsing PDF file: {str(e)}"
        )

    # 4. Chunking logic
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        chunks = splitter.split_text(extracted_text)
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while splitting the extracted text: {str(e)}"
        )
