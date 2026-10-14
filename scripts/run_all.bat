@echo off
echo ========================================================
echo Starting AI-Powered Cybersecurity Digital Twin
echo Starting Backend (FastAPI :8000) and Frontend (Vite :5173)...
echo ========================================================

start "Cyber Digital Twin - Backend (FastAPI)" cmd /k "%~dp0run_backend.bat"
start "Cyber Digital Twin - Frontend (Vite React)" cmd /k "%~dp0run_frontend.bat"

echo.
echo Both servers are launching in separate windows:
echo - Backend API & Docs: http://127.0.0.1:8000/api/v1/docs
echo - SOC Frontend Dashboard: http://localhost:5173
echo.
