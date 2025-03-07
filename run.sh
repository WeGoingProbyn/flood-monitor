#!/bin/bash

# Minimum required Python version
REQUIRED_PYTHON_VERSION="3.10"

# Check if the installed Python version meets the minimum requirement.
python3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10 or higher is required'" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "ERROR: Python $REQUIRED_PYTHON_VERSION or higher is required."
  exit 1
else
  echo "Minimum python version met..."
fi

# Check if a virtual environment directory (venv) exists; if not, create one
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Optionally, upgrade pip
pip install --upgrade pip

# Install the required packages from requirements.txt
echo "Installing requirements..."
pip install -r requirements.txt

# Run the Streamlit app
echo "Launching Streamlit..."
streamlit run main.py
