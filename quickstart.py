import os.path
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
# The ID of a sample presentation.
PRESENTATION_ID = "1OOvlh9s-sd5PHptLi0N3NGKxKYxNdOcPZLbcGcjL-go"

def resize_and_convert(image_path, size=(600, 450)):
    """Resize and convert image to a supported format (PNG)."""
    img = Image.open(image_path)
    img = img.resize(size)
    new_image_path = os.path.splitext(image_path)[0] + ".png"
    img.save(new_image_path, "PNG")
    return new_image_path

def main():
    """Shows basic usage of the Slides API.
    Prints the number of slides and elements in a sample presentation.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8000)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("slides", "v1", credentials=creds)
        presentation = service.presentations().get(presentationId=PRESENTATION_ID).execute()
        slides = presentation.get("slides")

        print(f"The presentation contains {len(slides)} slides:")

        i = 1
        while True:
            image_path = f"{i}.png"
            if not os.path.exists(image_path):
                break

            image = resize_and_convert(image_path)

            drive_service = build("drive", "v3", credentials=creds)
            file_metadata = {
                "name": image,
                "mimeType": "image/png"
            }
            media = MediaFileUpload(image, mimetype="image/png", resumable=True)
            image_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            drive_service.permissions().create(
                fileId=image_file['id'],
                body={
                    'type': 'anyone',
                    'role': 'reader',
                },
                fields='id',
            ).execute()
            
            requests = [
                {
                    "createSlide": {
                        "objectId": f"slide{i}",
                        "insertionIndex": i,
                        "slideLayoutReference": {
                            "predefinedLayout": "BLANK"
                        }
                    }
                },
                {
                    "createShape": {
                        "objectId": f"title{i}",
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": f"slide{i}",
                            "size": {
                                "height": {
                                    "magnitude": 1000000,
                                    "unit": "EMU"
                                },
                                "width": {
                                    "magnitude": 4572000,
                                    "unit": "EMU"
                                }
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": 0,
                                "translateY": 0,
                                "unit": "EMU"
                            }
                        }
                    }
                },
                {
                    "createShape": {
                        "objectId": f"text{i}",
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": f"slide{i}",
                            "size": {
                                "height": {
                                    "magnitude": 4143500,
                                    "unit": "EMU"
                                },
                                "width": {
                                    "magnitude": 4572000,
                                    "unit": "EMU"
                                }
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": 0,
                                "translateY": 1000000,
                                "unit": "EMU"
                            }
                        }
                    }
                },
                {
                    "createImage": {
                        "objectId": f"image{i}",
                        "url": f"https://drive.google.com/uc?id={image_file['id']}",
                        "elementProperties": {
                            "pageObjectId": f"slide{i}",
                            "size": {
                                "height": {
                                    "magnitude": 2812500,
                                    "unit": "EMU"
                                },
                                "width": {
                                    "magnitude": 3750000,
                                    "unit": "EMU"
                                }
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": 5297000, 
                                "translateY": 1265625,
                                "unit": "EMU"
                            }
                        }
                    }
                }
            ]
            i += 1
            service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

            

        webbrowser.open(f"https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit")

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()