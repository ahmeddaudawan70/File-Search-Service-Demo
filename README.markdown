# File Search Service

> This project was built as part of an interview process.

A FastAPI service that indexes files from a Google Drive folder into Elasticsearch and exposes a full-text search API and CLI. It supports CSV, TXT, PDF, and PNG files — including OCR for image-based content.

---

## Features

- Fetches files from a specified Google Drive folder via the Google Drive API (OAuth 2.0)
- Extracts text from:
  - **CSV / TXT** — direct UTF-8 decoding
  - **PDF** — `pdfplumber` for text-based PDFs
  - **PNG** — Tesseract OCR
- Indexes file name, content, and Drive URL into Elasticsearch on startup
- Full-text search across file names and content via a REST API (`/search`) and a CLI (`cli.py`)

---

## Project Structure

```
File-Search-Service/
├── main.py                  # FastAPI app entry point, startup indexing
├── cli.py                   # Command-line search interface
├── api/
│   └── routes.py            # /search endpoint
├── services/
│   ├── drive_client.py      # Google Drive file listing and download
│   ├── indexer.py           # Elasticsearch indexing and search
│   └── text_extractor.py    # Text extraction (PDF, PNG, CSV, TXT)
├── config/
│   └── settings.py          # Configuration (reads from environment variables)
├── requirements.txt
├── credentials.json         # Google Drive OAuth credentials (not in repo)
└── token.json               # Generated OAuth token (created at runtime)
```

---

## Prerequisites

### Python
Version 3.8 or higher.

### Google Drive API Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the **Google Drive API**
3. Create **OAuth 2.0 credentials** and download `credentials.json`
4. Place `credentials.json` in the project root

### Elasticsearch
Version 8.x recommended. Install on macOS:
```bash
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full
elasticsearch
```
> Preferably install manually — see [this guide](https://www.youtube.com/watch?v=-_YXiaETaVU&ab_channel=DataHeadGirl).

### Tesseract OCR
Required for PNG and image-based PDF extraction.
```bash
brew install tesseract
```

### Google Drive Folder
- Create or identify a Drive folder containing CSV, TXT, PDF, or PNG files
- Copy the folder ID from the URL:
  `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

---

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd File-Search-Service
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Your Google Drive Folder ID
Open `services/drive_client.py` and replace the placeholder:
```python
folder_id = "YOUR_FOLDER_ID_HERE"
```

### 5. Set Elasticsearch Credentials
Export these environment variables before running the app:
```bash
export ELASTICSEARCH_HOST=https://localhost:9200
export ELASTICSEARCH_USERNAME=elastic
export ELASTICSEARCH_PASSWORD=your_password_here
```
> The password is printed in the terminal when you first start Elasticsearch. Add these exports to `~/.zshrc` or `~/.bashrc` to persist them across sessions.

### 6. Authenticate with Google Drive
On first run, the app will open a browser window for OAuth. After approving, `token.json` is saved and used for all future runs.

---

## Running

```bash
source venv/bin/activate
python main.py
```

On startup, the service will:
1. Authenticate with Google Drive
2. Fetch and download all supported files from the configured folder
3. Extract text and index each file into Elasticsearch
4. Start the API server at `http://localhost:8000`

Expected console output:
```
INFO:services.drive_client:Files retrieved from Google Drive:
INFO:services.indexer:Indexed file: example.pdf
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Usage

### REST API

Search via `curl` (always quote the URL to avoid `zsh` globbing issues):
```bash
curl "http://localhost:8000/search?q=Samsung"
```

Example response:
```json
[
  {"name": "Samsung.pdf", "url": "https://drive.google.com/file/d/.../view"},
  {"name": "Samsung and Google.txt", "url": "https://drive.google.com/file/d/.../view"}
]
```

### CLI

```bash
python cli.py "Samsung"
```

Example output:
```
Samsung.pdf...https://drive.google.com/file/d/.../view
Samsung and Google.txt...https://drive.google.com/file/d/.../view
```

Returns `Empty` if no results are found.

### Swagger UI

Interactive API docs available at `http://localhost:8000/docs`.

---

## Troubleshooting

**Google Drive authentication fails**
- Delete `token.json` and rerun `python main.py` to re-authenticate
- Ensure `credentials.json` is present in the project root and the folder ID is correct

**Cannot connect to Elasticsearch**
- Verify it is running:
  ```bash
  curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD https://localhost:9200 --insecure
  ```
- Check Elasticsearch logs:
  ```bash
  cat /usr/local/var/log/elasticsearch/elasticsearch.log
  ```

**Empty search results**
- Confirm files were indexed:
  ```bash
  curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD "https://localhost:9200/files/_search?pretty" --insecure
  ```
- Clear the index and re-index:
  ```bash
  curl -u $ELASTICSEARCH_USERNAME:$ELASTICSEARCH_PASSWORD -X DELETE https://localhost:9200/files --insecure
  python main.py
  ```

**PDF content not searchable**
- Ensure Tesseract is installed (`brew install tesseract`)
- The service automatically falls back to OCR if `pdfplumber` extracts no text

**`curl` command fails in zsh**
- Always wrap the URL in double quotes:
  ```bash
  curl "http://localhost:8000/search?q=your_query"
  ```

---

## Notes

- `verify_certs=False` is used for the Elasticsearch connection — acceptable for local development, but use proper SSL certificates in production
- The OAuth redirect during authentication runs on port `3000` — ensure this port is available on first run
