# Traffic Analysis Toolkit

This project provides a local web application for analyzing and visualizing traffic data from Google Analytics 4 (GA4) CSV exports.

## Setup

1.  **Create a Virtual Environment:**
    In the project directory, create a Python virtual environment.
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the Environment:**
    Activate the virtual environment. You'll need to do this each time you open a new terminal to use the tool.
    ```bash
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install the necessary Python libraries.
    ```bash
    pip install pandas numpy matplotlib Flask
    ```

---

## How to Use

This tool (`app.py`) runs a local web server that provides a user-friendly interface to upload your CSV files and see the visualization directly on a webpage.

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
