## Google Sheets C2
This project demonstrates how to use Google Sheets as a Command and Control (C2) server to fetch and execute commands. The script connects to a Google Sheet, retrieves the latest command, and processes it accordingly.

## Prerequisites
1. **Google Cloud Project**
- Create a Google Cloud Project and enable the Google Sheets API.
- Create a service account and download the JSON key file.

2. **Google Sheet**
-Create a Google Sheet and share it with the service account email.

3. **Python Packages**
- Ensure you have the necessary Python packages installed:
```sh
pip install gspread oauth2client
```

## Setup
1. **Clone the repository**:

```sh
git clone https://github.com/Dyst0rti0n/Dyst0rti0n.github.io.git
cd Dyst0rti0n.github.io
```

2. Save your service account credentials JSON file in the project directory.

3. Update the `sheet_url` and `creds_json` variables in `google_sheets_c2.py` with your Google Sheet URL and the path to your service account JSON file.

## Usage
- Run the script to fetch and execute the latest command from the Google Sheet:

```sh
python google_sheets_c2.py
```

## Example
Here’s a basic example of what your Google Sheet might look like:

| Command | | --- | | echo "Hello, World!" | | ls -la |

The script will retrieve the latest command from the Google Sheet and print it to the console.

## Error Handling
The script includes basic error handling for:

- Google Sheets API errors
- File not found errors
- General exceptions

## Additional Enhancements
1. **Command Execution**: Expand the `main()` function to execute commands using Python's `subprocess` module.

2. **Scheduling**: Use scheduling libraries like `schedule` or set up a cron job (Linux) or Task Scheduler (Windows) to regularly check for new commands.

## License
This project is licensed under the MIT License. See the LICENSE file for details.