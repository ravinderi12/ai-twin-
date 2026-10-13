@echo off
echo ========================================================
echo Running Automated Test Suite (Pytest)...
echo ========================================================
cd /d "%~dp0\.."
python -m pytest backend/tests -v
pause
