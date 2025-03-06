# Flood Monitoring

An interactive web application built with Streamlit that lets users monitor flood-related data by selecting a river, town, and station. It queries the Environment Agency's flood-monitoring API to fetch data over the past 24 hours, and displays the results using charts and data tables.

## Features

- **Interactive UI:** Select a river, town, and station using dropdown menus.
- **Real-time Data:** Retrieves current flood monitoring measurements from the UK's flood-monitoring API.
- **Data Visualization:** Displays measurement data with line charts and data tables.
- **Rust Inspired Error Handling:** Uses an error module inspired by rust error handling to gracefully handle API errors and unexpected responses.

## Requirements

- **Python 3.10+**
- **Streamlit:** For the web interface.
- **Requests:** To make HTTP requests to the API.
- **Pandas:** For data manipulation and constructing data frames.

## Usage
- **Running the app:** Provided shell and batch scripts will setup virtual environment and install requirements if needed, the app will then be run.

**Linux:**
```bash
sh run.sh
```
**Windows**
```bash
run.bat
```

- Tested on Fedora 41 linux and windows 10.

