param([int]$Port=8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port $Port --reload
