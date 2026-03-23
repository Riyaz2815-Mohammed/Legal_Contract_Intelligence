import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Scope needed to create/edit files in Drive and Docs
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    load_dotenv()
    
    # Check if the secret JSON is in the .env file
    client_secret_json_str = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
    
    if not client_secret_json_str:
        print("\n[ERROR] Could not find GOOGLE_CLIENT_SECRET_JSON in your .env file.")
        print("Make sure you wrapped the JSON string in single quotes: GOOGLE_CLIENT_SECRET_JSON='{\"web\":{...}}'\n")
        return
        
    try:
        client_config = json.loads(client_secret_json_str)
    except json.JSONDecodeError:
        print("\n[ERROR] Failed to parse GOOGLE_CLIENT_SECRET_JSON.")
        print("Please make sure you copied the exact contents of the downloaded JSON file.\n")
        return

    # Use InstalledAppFlow with the client_config
    flow = InstalledAppFlow.from_client_config(
        client_config,
        SCOPES,
        # redirect_uri must match one configured in Google Cloud Console
        # Using a local server is the recommended way for desktop apps
    )
    
    print("\nOpening your browser to Google Login.")
    print("Please select your personal Google Account and grant the Drive permissions.")
    print("If you see a warning about an unverified app, click 'Advanced' -> 'Go to <app name>'.\n")
    
    # Run local server to authenticate and get the token
    creds = flow.run_local_server(
        port=0,
        access_type='offline',
        prompt='consent'
    )

    # Convert the credentials to JSON string format
    token_json_str = creds.to_json()
    
    # Append the token to the .env file
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Read existing content to ensure we don't duplicate
    with open(env_path, 'r') as f:
        existing_env = f.read()
        
    if 'GOOGLE_OAUTH_TOKEN_JSON=' in existing_env:
        print("\n[INFO] GOOGLE_OAUTH_TOKEN_JSON is already in .env. Please remove it first if you want to replace it.")
    else:
        with open(env_path, 'a') as f:
            # Ensure we start on a new line
            if existing_env and not existing_env.endswith('\n'):
                f.write('\n')
            f.write(f"GOOGLE_OAUTH_TOKEN_JSON='{token_json_str}'\n")
        print("\n" + "="*80)
        print("SUCCESS! Authorization complete.")
        print("="*80)
        print("\nThe token has been automatically added to your backend/.env file!")
        print("You can close this window/script and return to the chat.\n")

if __name__ == '__main__':
    main()