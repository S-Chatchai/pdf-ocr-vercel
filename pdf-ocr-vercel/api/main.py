# =============================================================================
# 3. api/main.py (Modified for Vercel serverless)
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import shutil
import uuid
import tempfile
from pathlib import Path
from typing import List
import json

# ✅ Configuration for Vercel
TYPHOON_API_KEY = os.environ.get('TYPHOON_OCR_API_KEY', 'your-api-key-here')

# ✅ Use temporary directory for serverless
def get_temp_dir():
    """Get a temporary directory for file operations"""
    return Path(tempfile.mkdtemp())

# ✅ FastAPI app setup
app = FastAPI(
    title="PDF OCR Service",
    description="A serverless PDF OCR service deployed on Vercel",
    version="1.0.0"
)

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic models
class OCRRequest(BaseModel):
    filename: str

class OCRResponse(BaseModel):
    filename: str
    text: str
    file_size: int
    success: bool

class UploadResponse(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    message: str

# ✅ Mock OCR function (replace with your actual OCR implementation)
def mock_ocr_document(file_path: str) -> str:
    """
    Mock OCR function - replace this with your actual OCR implementation
    For Vercel deployment, consider using:
    - Google Vision API
    - AWS Textract
    - Azure Cognitive Services
    """
    # This is a placeholder - implement your actual OCR logic here
    return f"Extracted text from {Path(file_path).name}\n\nThis is mock text extracted from the PDF. Replace this function with your actual OCR implementation."

# ✅ Root endpoint - serve the web interface
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF OCR Web App - Vercel Deployment</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 40px;
                max-width: 700px;
                width: 100%;
                text-align: center;
            }

            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
                font-weight: 300;
            }

            .upload-section {
                margin-bottom: 30px;
            }

            .file-input-wrapper {
                position: relative;
                display: inline-block;
                margin-bottom: 20px;
            }

            .file-input {
                position: absolute;
                opacity: 0;
                width: 100%;
                height: 100%;
                cursor: pointer;
            }

            .file-input-label {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 16px;
                font-weight: 500;
            }

            .file-input-label:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }

            .file-info {
                margin-top: 15px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                display: none;
            }

            .upload-btn {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
            }

            .upload-btn:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }

            .upload-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .loading {
                display: none;
                margin: 20px 0;
            }

            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .result-section {
                margin-top: 30px;
                text-align: left;
            }

            .result-box {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.5;
            }

            .error {
                background: #f8d7da;
                border-color: #f5c6cb;
                color: #721c24;
            }

            .vercel-badge {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #000;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF OCR Service</h1>
            <p style="color: #666; margin-bottom: 30px;">Deployed on Vercel ⚡</p>
            
            <div class="upload-section">
                <div class="file-input-wrapper">
                    <input type="file" id="fileInput" class="file-input" accept=".pdf" multiple>
                    <label for="fileInput" class="file-input-label">
                        📁 Choose PDF Files
                    </label>
                </div>
                
                <div class="file-info" id="fileInfo">
                    <div id="filesList"></div>
                </div>
                
                <button class="upload-btn" id="uploadBtn" onclick="uploadAndOCR()" disabled>
                    🚀 Upload & Extract Text
                </button>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing your PDF...</p>
            </div>

            <div class="result-section" id="resultSection" style="display: none;">
                <h3>Extracted Text:</h3>
                <div class="result-box" id="resultBox"></div>
            </div>
        </div>

        <a href="https://vercel.com" class="vercel-badge" target="_blank">
            Powered by Vercel
        </a>

        <script>
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const filesList = document.getElementById('filesList');
            const uploadBtn = document.getElementById('uploadBtn');
            const loading = document.getElementById('loading');
            const resultSection = document.getElementById('resultSection');
            const resultBox = document.getElementById('resultBox');

            let selectedFiles = [];

            // Handle file selection
            fileInput.addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                selectedFiles = files;
                updateFilesList();
                uploadBtn.disabled = selectedFiles.length === 0;
            });

            // Update files list display
            function updateFilesList() {
                if (selectedFiles.length === 0) {
                    fileInfo.style.display = 'none';
                    return;
                }

                fileInfo.style.display = 'block';
                filesList.innerHTML = `
                    <strong>Selected Files (${selectedFiles.length}):</strong><br>
                    ${selectedFiles.map(file => `• ${file.name} (${formatFileSize(file.size)})`).join('<br>')}
                `;
            }

            // Format file size
            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }

            // Upload and OCR function
            async function uploadAndOCR() {
                if (selectedFiles.length === 0) {
                    alert('Please select PDF files first!');
                    return;
                }

                // Show loading state
                loading.style.display = 'block';
                uploadBtn.disabled = true;
                resultSection.style.display = 'none';

                try {
                    const formData = new FormData();
                    selectedFiles.forEach(file => {
                        formData.append('files', file);
                    });

                    const response = await fetch('/api/upload-and-ocr', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Display results
                        let resultsText = '';
                        data.results.forEach((result, index) => {
                            resultsText += `=== ${result.original_filename} ===\\n`;
                            resultsText += result.text + '\\n\\n';
                        });

                        if (data.failed_files.length > 0) {
                            resultsText += '=== FAILED FILES ===\\n';
                            data.failed_files.forEach(failed => {
                                resultsText += `${failed.filename}: ${failed.error}\\n`;
                            });
                        }

                        resultBox.textContent = resultsText;
                        resultBox.className = 'result-box';
                        resultSection.style.display = 'block';
                    } else {
                        throw new Error(data.detail || 'Processing failed');
                    }

                } catch (error) {
                    resultBox.textContent = `Error: ${error.message}`;
                    resultBox.className = 'result-box error';
                    resultSection.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                    uploadBtn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ✅ Simplified upload and OCR endpoint for serverless
@app.post("/api/upload-and-ocr")
async def upload_and_ocr(files: List[UploadFile] = File(...)):
    """Upload and process PDF files in one step (optimized for serverless)"""
    
    results = []
    failed_files = []
    temp_dir = get_temp_dir()
    
    try:
        for file in files:
            try:
                # Validate file type
                if not file.filename.lower().endswith('.pdf'):
                    failed_files.append({
                        "filename": file.filename,
                        "error": "Only PDF files are allowed"
                    })
                    continue
                
                # Save file temporarily
                unique_filename = f"{uuid.uuid4()}.pdf"
                file_path = temp_dir / unique_filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Process with OCR
                extracted_text = mock_ocr_document(str(file_path))
                file_size = file_path.stat().st_size
                
                results.append({
                    "filename": unique_filename,
                    "original_filename": file.filename,
                    "text": extracted_text,
                    "file_size": file_size,
                    "success": True
                })
                
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
    
    finally:
        # Clean up temporary files
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
    
    return {
        "results": results,
        "failed_files": failed_files,
        "total_processed": len(results),
        "total_failed": len(failed_files),
        "message": f"Processed {len(results)} files successfully, {len(failed_files)} failed"
    }

# ✅ Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PDF OCR Service",
        "platform": "Vercel",
        "version": "1.0.0",
        "api_key_configured": bool(TYPHOON_API_KEY and TYPHOON_API_KEY != 'your-api-key-here')
    }

# ✅ Export the app for Vercel
# This is the entry point for Vercel
handler = app