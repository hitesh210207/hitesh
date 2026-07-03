import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def make_minimal_pdf():
    # A minimal valid PDF containing the text "Hello World from Chunks!"
    return (
        b'%PDF-1.4\n'
        b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n'
        b'4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n'
        b'5 0 obj\n<< /Length 44 >>\nstream\n'
        b'BT\n/F1 12 Tf\n72 712 Td\n(Hello World from Chunks!) Tj\nET\n'
        b'endstream\nendobj\n'
        b'xref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000293 00000 n\n'
        b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n386\n%%EOF'
    )

def test_welcome_json():
    print("Testing GET / (JSON welcome)...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome" in data["message"]
    print("✓ Welcome JSON test passed!")

def test_welcome_html():
    print("Testing GET / (HTML Dashboard)...")
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Recursive Text Splitter Dashboard" in response.text
    print("✓ Welcome HTML test passed!")

def test_split_text_valid():
    print("Testing POST /split (valid parameters)...")
    payload = {
        "text": "This is a simple text that we want to split into multiple small chunks.",
        "chunk_size": 20,
        "chunk_overlap": 5
    }
    response = client.post("/split", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert "total_chunks" in data
    assert data["total_chunks"] > 0
    print(f"✓ Split Text test passed! Chunks: {data['chunks']}")

def test_split_text_defaults():
    print("Testing POST /split (default parameters)...")
    # Sending only text, chunk_size and chunk_overlap should default to 50 and 10
    payload = {
        "text": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python."
    }
    response = client.post("/split", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert "total_chunks" in data
    print("✓ Split Text defaults test passed!")

def test_split_text_invalid_overlap():
    print("Testing POST /split (invalid parameters: overlap >= size)...")
    payload = {
        "text": "Sample text",
        "chunk_size": 20,
        "chunk_overlap": 20
    }
    response = client.post("/split", json=payload)
    assert response.status_code == 400
    assert "strictly less than chunk_size" in response.json()["detail"]
    print("✓ Invalid parameters error handling test passed!")

def test_split_text_invalid_size():
    print("Testing POST /split (invalid parameters: size <= 0)...")
    payload = {
        "text": "Sample text",
        "chunk_size": -5,
        "chunk_overlap": 0
    }
    response = client.post("/split", json=payload)
    assert response.status_code == 400
    assert "positive integer greater than 0" in response.json()["detail"]
    print("✓ Invalid chunk size error handling test passed!")

def test_split_text_empty():
    print("Testing POST /split (empty text)...")
    payload = {
        "text": "   ",
        "chunk_size": 50,
        "chunk_overlap": 10
    }
    response = client.post("/split", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
    print("✓ Empty text error handling test passed!")

def test_split_pdf_valid():
    print("Testing POST /split-pdf (valid mock PDF file)...")
    pdf_bytes = make_minimal_pdf()
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"chunk_size": 15, "chunk_overlap": 5}
    response = client.post("/split-pdf", files=files, data=data)
    
    assert response.status_code == 200
    res_data = response.json()
    assert "chunks" in res_data
    assert "total_chunks" in res_data
    # Let's verify that the text extracted matches Hello World
    any_chunk_has_text = any("Hello World" in c for c in res_data["chunks"])
    assert any_chunk_has_text, f"Chunks did not contain extracted text: {res_data['chunks']}"
    print(f"✓ PDF Split test passed! Chunks: {res_data['chunks']}")

def test_split_pdf_invalid_format():
    print("Testing POST /split-pdf (invalid format)...")
    files = {"file": ("test.txt", b"plain text content", "text/plain")}
    data = {"chunk_size": 50, "chunk_overlap": 10}
    response = client.post("/split-pdf", files=files, data=data)
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]
    print("✓ PDF invalid format error handling test passed!")

if __name__ == "__main__":
    print("=== Running FastAPI Text Splitter Tests ===")
    test_welcome_json()
    test_welcome_html()
    test_split_text_valid()
    test_split_text_defaults()
    test_split_text_invalid_overlap()
    test_split_text_invalid_size()
    test_split_text_empty()
    test_split_pdf_valid()
    test_split_pdf_invalid_format()
    print("=== All Tests Passed Successfully! ===")
