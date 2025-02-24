@echo off
chcp 65001

:: Check if the virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Check if dependencies are installed
pip show tkinterdnd2 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing tkinterdnd2...
    pip install tkinterdnd2==0.3.0
)

:: Check if nest_asyncio is installed
pip show nest_asyncio >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing nest_asyncio...
    pip install nest_asyncio==1.5.8
)

:: Check if OpenAI SDK is installed
pip show openai >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing OpenAI SDK...
    pip install --upgrade "openai>=1.0"
)

:: Check if requests is installed
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests...
    pip install --upgrade requests
)

:: Run the program
echo Starting the program...
python main.py

:: Pause to view output
pause 