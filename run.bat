@echo off

REM Check if Python version is at least 3.7
python -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10 or higher is required'" 
if %errorlevel% neq 0 (
  echo ERROR: Python 3.10 or higher is required.
  pause
  exit /b 1
) else (
  echo Python minimum version met...
)

REM Check if the virtual environment exists by looking for the activation script
if not exist ".venv\Scripts\activate.bat" (
  echo Creating virtual environment...
  python -m venv .venv
)

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install the required packages from requirements.txt
echo Installing requirements...
pip install -r requirements.txt

REM Launch the Streamlit app
echo Launching Streamlit...
streamlit run main.py

pause
