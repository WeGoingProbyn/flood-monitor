#!/bin/bash

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
