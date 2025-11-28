# Traffic Analysis Toolkit

This project contains two tools for analyzing and visualizing traffic data from Google Analytics 4 (GA4) CSV exports. You can either use a command-line script to generate a PDF report or a local web application for an interactive experience.

## General Setup

Both tools share the same setup process. You only need to do this once.

1.  **Create a Virtual Environment:**
    In the project directory, create a Python virtual environment.
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the Environment:**
    Activate the virtual environment. You'll need to do this each time you open a new terminal to use these tools.
    ```bash
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install the necessary Python libraries for both tools.
    ```bash
    pip install pandas numpy matplotlib Flask
    ```

---

## Option 1: Use the Command-Line Tool

This tool (`traffic_analyzer_tool.py`) generates a PDF report comparing traffic data from two CSV files.

### How to Use

1.  Make sure your virtual environment is active.
2.  Run the script from your terminal, providing the paths to the two CSV files.

### Command Format

```bash
python3 traffic_analyzer_tool.py <path_to_older_file.csv> <path_to_newer_file.csv> [options]
```

#### Options

*   `-o, --output <filename.pdf>`: (Optional) Specify a name for the output PDF report. Defaults to `Traffic_Comparison_Report.pdf`.

### Example

```bash
python3 traffic_analyzer_tool.py \
  'Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2024.csv' \
  'Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2025.csv' \
  -o My_Analysis.pdf
```

This command will create a new PDF file named `My_Analysis.pdf` in the project directory.

---

## Option 2: Use the Web Application

This tool (`app.py`) runs a local web server that provides a user-friendly interface to upload your CSV files and see the visualization directly on a webpage.

### How to Use

1.  **Start the Server:**
    Make sure your virtual environment is active, then run the `app.py` script.
    ```bash
    python3 app.py
    ```

2.  **Access the Application:**
    Once the server is running, your terminal will display a message like `* Running on http://127.0.0.1:5001/`. Open your web browser and navigate to that URL:
    [http://127.0.0.1:5001/](http://127.0.0.1:5001/)

3.  **Upload Files:**
    On the webpage, you will see two upload fields. Use them to select the older (Year 1) and newer (Year 2) CSV files from your computer.

4.  **View Results:**
    Click the "Generate Visualization" button. The application will process the files and display the traffic comparison chart on a new results page.

5.  **Stop the Server:**
    To stop the web server, return to your terminal and press `Ctrl+C`.
