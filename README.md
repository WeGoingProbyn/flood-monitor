# Flood Monitoring

An interactive web application built with Streamlit that lets users monitor flood-related data by selecting a river, town, and station. It queries the UK's Environment Agency's flood-monitoring API to fetch data over the past 24 hours, and displays the results using charts and data tables.

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
chmod +x ./run.sh
./run.sh
```
**Windows**
```bash
run.bat
```

- Tested on Fedora 41 linux and windows 10.

## Known issues
- When trying to terminate the process from console on windows after closing the tab in your browser, CTRL+C will take a long time to kill the process, this can be fixed by re-opening the tab and retrying the kill signal. see: https://discuss.streamlit.io/t/cant-stop-streamlit-app-using-ctrl-c-if-the-app-has-been-closed-in-the-browser/38738
