# Chunks.ai: Recursive Text & PDF Splitter API

Chunks.ai is a FastAPI web application designed to recursively split raw text and uploaded PDF files into chunks using LangChain's `RecursiveCharacterTextSplitter`. It features a premium, interactive glassmorphic web dashboard (Vanilla CSS) for direct browser testing and content-negotiated endpoints for JSON API clients.

---

## ✨ Features

- **Interactive Dashboard**: A responsive, modern dark-mode UI with tabs for raw text input and drag-and-drop PDF uploads.
- **Content Negotiation**: Serving the web dashboard on browser requests (`GET /`) and descriptive JSON metadata for API clients.
- **LangChain Splitter Integration**: Utilizes `RecursiveCharacterTextSplitter` to handle semantic boundaries and custom overlaps.
- **PDF Extraction**: Extracts text dynamically from multi-page PDFs using `pypdf`.
- **Input Validation**: Restricts chunk parameters to valid bounds (`chunk_size > 0`, `chunk_overlap >= 0`, `chunk_overlap < chunk_size`).
- **Comprehensive Test Suite**: Local API verification using `fastapi.testclient`.

---

## 🛠️ Project Structure

```text
fastapi_text_splitter/
├── templates/
│   └── index.html      # Interactive frontend dashboard (Vanilla CSS)
├── Dockerfile          # Multi-platform Docker configuration
├── main.py             # FastAPI entrypoint, validation, routes, and split logic
├── requirements.txt    # Project Python dependencies
├── test_app.py         # Testing suite for automated verification
└── README.md           # Documentation
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+ installed on your system.

### 1. Create a Virtual Environment and Install Dependencies
In your terminal, navigate to the project directory and run:
```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip and install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run the Verification Tests
Before starting the server, run the automated test suite to ensure everything is set up properly:
```bash
python test_app.py
```

### 3. Launch the FastAPI Server
Run the FastAPI development server:
```bash
uvicorn main:app --reload --port 8000
```
Open **`http://localhost:8000`** in your web browser to access the interactive dashboard.

---

## 🔌 API Documentation

Detailed Swagger UI documentation is available at **`http://localhost:8000/docs`**.

### 1. Welcome Endpoint
- **URL**: `GET /`
- **Response (HTML)**: Interactive Web Dashboard (rendered when requested by a browser).
- **Response (JSON)**:
  ```json
  {
      "message": "Welcome to the Chunks.ai Text Splitter API!",
      "docs_url": "/docs",
      "interactive_ui_url": "/",
      "usage": {
          "text_splitter": "POST /split (JSON payload: text, chunk_size, chunk_overlap)",
          "pdf_splitter": "POST /split-pdf (Multipart Form: file, chunk_size, chunk_overlap)"
      }
  }
  ```

### 2. Split Raw Text
- **URL**: `POST /split`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
      "text": "Your large input text goes here...",
      "chunk_size": 50,
      "chunk_overlap": 10
  }
  ```
- **Response**:
  ```json
  {
      "chunks": ["Your large input text", "text goes here..."],
      "total_chunks": 2
  }
  ```

### 3. Split PDF File
- **URL**: `POST /split-pdf`
- **Headers**: `Content-Type: multipart/form-data`
- **Form Data Parameters**:
  - `file`: PDF file upload binary.
  - `chunk_size`: `50` (optional parameter).
  - `chunk_overlap`: `10` (optional parameter).
- **Response**:
  ```json
  {
      "chunks": ["Extracted text from PDF...", "more split chunks..."],
      "total_chunks": 12
  }
  ```

---

## 🐳 Docker and Production Deployment

### Option 1: Hugging Face Spaces (Docker SDK)

1. Log in to [Hugging Face](https://huggingface.co/) and create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space).
2. Set Space name as `assignment_1`.
3. Select **Docker** as the Space SDK and choose **Blank** under Docker templates.
4. Set visibility to **Public**.
5. Upload or push all project files (`main.py`, `requirements.txt`, `Dockerfile`, `templates/index.html`) to your Space's repository. Hugging Face will build the Docker container and start running the app automatically.

### Option 2: Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and create a new **Web Service**.
2. Link your Git repository.
3. Render will automatically detect the `Dockerfile` in the root folder, compile it, and launch it live.
