import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/presentations"]

# The ID of a sample presentation.
PRESENTATION_ID = "1OOvlh9s-sd5PHptLi0N3NGKxKYxNdOcPZLbcGcjL-go"

def main():
    """Shows basic usage of the Slides API.
    Prints the number of slides and elements in a sample presentation.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("slides", "v1", credentials=creds)

        # Call the Slides API
        presentation = service.presentations().get(presentationId=PRESENTATION_ID).execute()
        slides = presentation.get("slides")

        print(f"The presentation contains {len(slides)} slides:")
        for i, slide in enumerate(slides):
            print(f"- Slide #{i + 1} contains {len(slide.get('pageElements'))} elements.")

        # Create new slides and add titles to them
        titles = ["testing1", "testing2", "testing3"]
        for i, title in enumerate(titles):
            requests = [
                {
                    "createSlide": {
                        "objectId": f"slide{i+1}",
                        "insertionIndex": i+1,
                        "slideLayoutReference": {
                            "predefinedLayout": "TITLE_AND_TWO_COLUMNS"
                        },
                        "placeholderIdMappings": [
                            {
                                "layoutPlaceholder": {
                                    "type": "TITLE",
                                    "index": 0
                                },
                                "objectId": f"title{i+1}"
                            }
                        ]
                    }
                },
                {
                    "insertText": {
                        "objectId": f"title{i+1}",
                        "text": title,
                        "insertionIndex": 0
                    }
                }
            ]
            service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()