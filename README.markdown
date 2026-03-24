# File Search Service

> This project was built as part of an interview process.

This project is a FastAPI-based application that retrieves files from a specified Google Drive folder, extracts text from supported file types (CSV, TXT, PDF, PNG), indexes them in Elasticsearch, and provides a search API to query the files by content or name. The application supports searching via a REST API (`/search` endpoint) and a command-line interface (CLI).

## Features
- **File Retrieval**: Fetches files (CSV, TXT, PDF, PNG) from a Google Drive folder using the Google Drive API.
- **Text Extraction**: Extracts text from:
  - CSV and TXT files (direct text).
  - PDF files (using `pdfplumber` with Tesseract OCR fallback for image-based PDFs).
  - PNG files (using Tesseract OCR).
- **Indexing**: Stores file metadata and extracted text in Elasticsearch for efficient searching.
- **Search**: Provides a `/search` API endpoint and CLI to query files by content or name.

## Prerequisites
Before setting up the project, ensure you have the following:

- **Python**: Version 3.8 or higher.
- **Google Drive API Credentials**:
  - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
  - Enable the Google Drive API.
  - Create OAuth 2.0 credentials and download the `credentials.json` file.
  - Place `credentials.json` in the project root directory.
- **Elasticsearch**:
  - Install and run Elasticsearch locally (version 8.x recommended).
  - Default configuration: `https://localhost:9200` with username `elastic` and password `what you got from the terminal`.
  - For macOS, install via Homebrew: (Preferably install manually,https://www.youtube.com/watch?v=-_YXiaETaVU&ab_channel=DataHeadGirl)
    ```bash
    brew tap elastic/tap
    brew install elastic/tap/elasticsearch-full
    elasticsearch
    ```
- **Tesseract OCR**:
  - Install Tesseract for PNG and image-based PDF text extraction.
  - On macOS:
    ```bash
    brew install tesseract
    ```
- **Google Drive Folder**:
  - A Google Drive folder containing files (CSV, TXT, PDF, PNG) to index.
  - Note the folder ID from the URL (e.g., `1AbCdEfGhIjKlMnOpQrStUv` from `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUv`).

## Dependencies
The project requires the following Python packages, listed in `requirements.txt`:

```
fastapi
uvicorn
google-auth-oauthlib
google-api-python-client
elasticsearch
pytesseract
Pillow
pdfplumber
click
```

Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Project Structure
- `main.py`: FastAPI application entry point, initializes services and indexes files on startup.
- `cli.py`: Command-line interface for searching indexed files.
- `api/routes.py`: Defines the `/search` FastAPI endpoint.
- `services/drive_client.py`: Handles Google Drive file retrieval and content download.
- `services/indexer.py`: Manages Elasticsearch indexing and search.
- `services/text_extractor.py`: Extracts text from files using `pdfplumber` and Tesseract.
- `config/settings.py`: Configuration file for Google Drive and Elasticsearch settings.
- `credentials.json`: Google Drive API credentials (not included in repository).
- `token.json`: Generated OAuth token (created after authentication).

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Drive**:
   - Place `credentials.json` in the project root.
   - Update `services/drive_client.py` with your Google Drive folder ID:
     ```python
     folder_id = "your_folder_id_here"  # Replace with actual folder ID
     ```
   - Ensure the folder contains CSV, TXT, PDF, or PNG files.

5. **Configure Elasticsearch**:
   - Ensure Elasticsearch is running on `https://localhost:9200`.
   - Set credentials as environment variables:
     ```bash
     export ELASTICSEARCH_HOST=https://localhost:9200
     export ELASTICSEARCH_USERNAME=elastic
     export ELASTICSEARCH_PASSWORD=your_password_here
     ```

6. **Authenticate with Google Drive**:
   - Run `main.py` to initiate OAuth authentication:
     ```bash
     python main.py
     ```
   - Follow the browser prompt to authenticate and save the `token.json` file.

## Running the Application
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Start the FastAPI server:
   ```bash
   python main.py
   ```
   - The server runs on `http://0.0.0.0:8000`.
   - On startup, it retrieves files from the specified Google Drive folder, extracts text, and indexes them in Elasticsearch.
   - Console output will show:
     ```
     INFO:services.drive_client:Files retrieved from Google Drive:
     INFO:services.indexer:Indexed file: ...
     INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
     ```

## Testing the Application

### Using `curl`
Test the search endpoint with `curl`. The URL must be quoted to avoid `zsh` globbing issues with the `?` character.

- **Search for files containing "Samsung"**:
  ```bash
  curl "http://0.0.0.0:8000/search?q=Samsung"
  ```
  **Example Output**:
  ```json
  [
      {"name": "Samsung.pdf", "url": "https://drive.google.com/file/d/1B7mTwFAg_M-zthC9SJ0uP1ArqOHLh3LV/view?usp=drivesdk"},
      {"name": "Samsung and Google.txt", "url": "https://drive.google.com/file/d/1Z8cJoZMcaTiq4pR65GSHNkzMpdBttLpL/view?usp=drivesdk"},
      {"name": "Galaxy S24.png", "url": "https://drive.google.com/file/d/1LKDIbIsWKUqeAYumKpalZtVy2dPP1HFW/view?usp=drivesdk"},
      ...
  ]
  ```

- **Search for all files**:
  ```bash
  curl "http://0.0.0.0:8000/search?q=*"
  ```

- **Search for other terms** (e.g., "Iphone" or "Galaxy"):
  ```bash
  curl "http://0.0.0.0:8000/search?q=Iphone"
  curl "http://0.0.0.0:8000/search?q=Galaxy"
  ```

- **Alternative Host**:
  If `0.0.0.0` doesn’t work, try `localhost`:
  ```bash
  curl "http://localhost:8000/search?q=Samsung"
  ```

- **Verbose Output for Debugging**:
  ```bash
  curl -v "http://0.0.0.0:8000/search?q=Samsung"
  ```

### Using Python CLI
The CLI (`cli.py`) allows searching directly from the command line.

- **Search for files containing "Samsung"**:
  ```bash
  python cli.py "Samsung"
  ```
  **Example Output**:
  ```
  Samsung.pdf...https://drive.google.com/file/d/1B7mTwFAg_M-zthC9SJ0uP1ArqOHLh3LV/view?usp=drivesdk
  Samsung and Google.txt...https://drive.google.com/file/d/1Z8cJoZMcaTiq4pR65GSHNkzMpdBttLpL/view?usp=drivesdk
  Galaxy S24.png...https://drive.google.com/file/d/1LKDIbIsWKUqeAYumKpalZtVy2dPP1HFW/view?usp=drivesdk
  ...
  ```

- **Search for other terms**:
  ```bash
  python cli.py "Iphone"
  python cli.py "Galaxy"
  ```

### Using Swagger UI
Access the interactive API documentation:
1. Open `http://localhost:8000/docs` in a browser.
2. Use the `/search` endpoint to test queries (e.g., `q=Samsung`).

## Troubleshooting
- **Google Drive Authentication**:
  - If authentication fails, delete `token.json` and rerun `python main.py` to re-authenticate.
  - Ensure `credentials.json` is valid and the folder ID in `services/drive_client.py` is correct.
- **Elasticsearch Connection**:
  - Verify Elasticsearch is running:
    ```bash
    curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD https://localhost:9200 --insecure
    ```
  - Check logs if indexing fails:
    ```bash
    cat /usr/local/var/log/elasticsearch/elasticsearch.log
    ```
- **Empty Search Results**:
  - Check indexed files:
    ```bash
    curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD https://localhost:9200/files/_search?pretty --insecure
    ```
  - Clear the index and re-run:
    ```bash
    curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD -X DELETE https://localhost:9200/files --insecure
    python main.py
    ```
- **PDF Content Not Searchable**:
  - If PDFs are image-based, ensure `services/text_extractor.py` includes the OCR fallback (using Tesseract).
  - Test extraction locally:
    ```bash
    python test_pdf_extraction.py Samsung.pdf
    ```
- **Curl Command Fails**:
  - Use quotes around the URL to avoid `zsh` globbing:
    ```bash
    curl "http://0.0.0.0:8000/search?q=Samsung"
    ```
  - Check server logs for errors:
    ```bash
    python main.py
    ```

## Notes
- The application uses `verify_certs=False` for Elasticsearch, which generates `InsecureRequestWarning` messages. This is safe for local testing but should be addressed with proper SSL certificates in production.
- Ensure Tesseract and `pdfplumber` are installed for PDF and PNG text extraction.
- The search query matches file names and content case-insensitively with fuzzy matching.