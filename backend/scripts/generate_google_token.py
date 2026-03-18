"""
Script to generate a Google Drive Refresh Token for personal account use.
Requirements: google-auth-oauthlib

Instructions:
1. Go to https://console.cloud.google.com/
2. Enable "Google Drive API".
3. Configure "OAuth consent screen":
   - User Type: External
   - App Name: Newsletter Herald
   - Scopes: Add 'https://www.googleapis.com/auth/drive'
   - Test Users: Add your own email address.
4. Go to "Credentials":
   - Create Credentials -> OAuth client ID
   - Application Type: Desktop App
   - Name: Herald CLI
5. Copy the Client ID and Client Secret into this script or environment.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    client_id = input("Enter your Google Client ID: ").strip()
    client_secret = input("Enter your Google Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required.")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # This will open a browser window for authentication
    creds = flow.run_local_server(port=0)

    print("\n" + "="*50)
    print("SUCCESS! Add these to your backend/.env file:")
    print("="*50)
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("="*50)

if __name__ == "__main__":
    main()
