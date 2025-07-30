# Urzasight Backend

Flask API server for OCR and LLM processing of manga text.

## Setup

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.template .env
# Edit .env with your API keys
```

3. Run server:
```bash
python app.py
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/process` - Process manga image (OCR + Analysis)

## Testing

Start the server and test with:
```bash
curl http://localhost:5000/health
```

Should return: `{"status":"healthy","service":"urzasight-backend"}`
