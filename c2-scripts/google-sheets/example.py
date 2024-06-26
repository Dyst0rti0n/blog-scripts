import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys

def get_latest_command(sheet_url, creds_json):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(sheet_url).sheet1
        
        commands = sheet.get_all_records()
        
        if commands:
            return commands[-1]['Command']
        else:
            return None

    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API error: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Credentials file not found: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    sheet_url = 'YOUR_GOOGLE_SHEET_URL'
    creds_json = 'path_to_your_creds.json'
    
    command = get_latest_command(sheet_url, creds_json)
    
    if command:
        print(f"Command: {command}")
        # Here you can add functionality to execute the command or process it as needed
        # execute_command(command)
    else:
        print("No command found or an error occurred.")

if __name__ == "__main__":
    main()
