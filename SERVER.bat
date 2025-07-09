@echo off
cd /d "D:\webchat"
call venv\Scripts\activate
uvicorn app:app --reload --host 0.0.0.0 --port 8001
