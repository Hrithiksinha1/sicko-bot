@echo off
echo Starting Streamlit Frontend...
echo.
echo Make sure the backend server is running first!
echo Backend: cd backend ^&^& python main.py
echo.
cd /d %~dp0
streamlit run app.py

