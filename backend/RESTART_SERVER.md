# Server Restart Required

The backend code has been updated. Please restart the FastAPI server to pick up the changes:

1. Stop the current server (Ctrl+C if running in terminal)
2. Restart it:
   ```bash
   cd backend
   python main.py
   ```

Or if using uvicorn directly:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag will auto-reload on code changes.

