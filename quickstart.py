import os.path
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image
from point_maker import get_presentation
from uuid import uuid4

sample_text = "Good morning, everyone. Today, I'm excited to talk to you about mitochondria, often called the powerhouse of the cell. Mitochondria are tiny organelles found in almost every cell in our bodies. They play a crucial role in generating energy by converting glucose and oxygen into ATP, which is the energy currency cells use for their functions. But that's not all—they also help regulate cell growth, death, and even have their own DNA, which is fascinating because it suggests they were once independent organisms billions of years ago. Understanding mitochondria is key to learning how our cells, and ultimately our bodies, function. Thank you!"
presentation_text = get_presentation(sample_text)

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

        if slides is not None:
            print(f"The presentation contains {len(slides)} slides:")
        else:
            print("No slides found in the presentation.")

        # Create title slide
        title_slide_request = [
            {
                "createSlide": {
                    "objectId": "titleSlide",
                    "insertionIndex": 0,
                    "slideLayoutReference": {
                        "predefinedLayout": "BLANK"
                    }
                }
            },
            {
                "createShape": {
                    "objectId": "titleTextBox",
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": "titleSlide",
                        "size": {
                            "height": {
                                "magnitude": 1000000,
                                "unit": "EMU"
                            },
                            "width": {
                                "magnitude": 6000000,
                                "unit": "EMU"
                            }
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 7200000 / 2 - 6000000 / 2,  # Subtract half of the width from half of the slide's width
                            "translateY": 4050000 / 2 - 1000000 / 2,  # Subtract half of the height from half of the slide's height
                            "unit": "EMU"
                        }
                    }
                }
            },
            {
                "insertText": {
                    "objectId": "titleTextBox",
                    "insertionIndex": 0,
                    "text": presentation_text[0]
                }
            },
            {
                "updateTextStyle": {
                    "objectId": "titleTextBox",
                    "style": {
                        "bold": True,
                        "fontSize": {
                            "magnitude": 50,  # Increase the font size
                            "unit": "PT"
                        }
                    },
                    "textRange": {
                        "type": "ALL"
                    },
                    "fields": "bold,fontSize"
                }
            }
        ]
        service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": title_slide_request}).execute()
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        for i, slide_content in enumerate(presentation_text[1:], start=1):
            slide_id = f"slide{i}"
            title_id = f"title{i}"

            slide_request = [
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "insertionIndex": i,
                        "slideLayoutReference": {
                            "predefinedLayout": "BLANK"
                        }
                    }
                },
                {
                    "createShape": {
                        "objectId": title_id,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {
                                "height": {
                                    "magnitude": 1000000,
                                    "unit": "EMU"
                                },
                                "width": {
                                    "magnitude": 7200000,  # Make the textbox as long as the width
                                    "unit": "EMU"
                                }
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": 0,  # Position the textbox at the left of the screen
                                "translateY": 0,  # Position the textbox at the top of the screen
                                "unit": "EMU"
                            }
                        }
                    }
                },
                {
                    "insertText": {
                        "objectId": title_id,
                        "insertionIndex": 0,
                        "text": slide_content[0]  # Use the first string in each element as the title
                    }
                },
                {
                    "updateTextStyle": {
                        "objectId": title_id,
                        "style": {
                            "bold": True,
                            "fontSize": {
                                "magnitude": 30,  # Decrease the font size
                                "unit": "PT"
                            }
                        },
                        "textRange": {
                            "type": "ALL"
                        },
                        "fields": "bold,fontSize"
                    }
                }
            ]
            

            # Create a new text box for each bullet point
            for j, bullet_point in enumerate(slide_content[1:], start=1):
                bullet_id = f"bullet{i}_{j}"

                bullet_request = [
                    {
                        "createShape": {
                            "objectId": bullet_id,
                            "shapeType": "TEXT_BOX",
                            "elementProperties": {
                                "pageObjectId": slide_id,
                                "size": {
                                    "height": {
                                        "magnitude": 1000000,
                                        "unit": "EMU"
                                    },
                                    "width": {
                                        "magnitude": 5000000,  
                                        "unit": "EMU"
                                    }
                                },
                                "transform": {
                                    "scaleX": 1,
                                    "scaleY": 1,
                                    "translateX": 0,  # Position the textbox at the left of the screen
                                    "translateY": 700000 * j,  # Position the textbox below the previous one with less gap
                                    "unit": "EMU"
                                }
                            }
                        }
                    },
                    {
                        "insertText": {
                            "objectId": bullet_id,
                            "insertionIndex": 0,
                            "text": f"• {bullet_point}"  # Add a bullet point before the text
                        }
                    },
                    {
                        "updateTextStyle": {
                            "objectId": bullet_id,
                            "style": {
                                "fontSize": {
                                    "magnitude": 15,  # Decrease the font size more
                                    "unit": "PT"
                                }
                            },
                            "textRange": {
                                "type": "ALL"
                            },
                            "fields": "fontSize"
                        }
                    },
                ]

                slide_request.extend(bullet_request)
            
            # Upload the image to Google Drive
            image_path = f"{i}.png"
            if os.path.exists(image_path):
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

                image_id = f"image_{uuid4().hex}"  # Generate unique image ID

                slide_request.append({
                    "createImage": {
                        "objectId": image_id,
                        "url": f"https://drive.google.com/uc?id={image_file['id']}",
                        "elementProperties": {
                            "pageObjectId": slide_id,
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
                })
                service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": slide_request}).execute()

        # i = 1
        # while True:
        #     image_path = f"{i}.png"
        #     if not os.path.exists(image_path):
        #         break

        #     image = resize_and_convert(image_path)

        #     drive_service = build("drive", "v3", credentials=creds)
        #     file_metadata = {
        #         "name": image,
        #         "mimeType": "image/png"
        #     }
        #     media = MediaFileUpload(image, mimetype="image/png", resumable=True)
        #     image_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        #     drive_service.permissions().create(
        #         fileId=image_file['id'],
        #         body={
        #             'type': 'anyone',
        #             'role': 'reader',
        #         },
        #         fields='id',
        #     ).execute()
            
        #     requests = [
        #     ]
        #     service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

        #     i += 1

        webbrowser.open(f"https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit")

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()

# sample_text = "Malcolm X was one of the most dynamic, dramatic and influential figures of the civil rights era..."
# presentation_text = get_presentation(sample_text)

# # If modifying these scopes, delete the file token.json.
# SCOPES = [
#     "https://www.googleapis.com/auth/presentations",
#     "https://www.googleapis.com/auth/drive.file",
#     "https://www.googleapis.com/auth/drive"
# ]
# # The ID of a sample presentation.
# PRESENTATION_ID = "1OOvlh9s-sd5PHptLi0N3NGKxKYxNdOcPZLbcGcjL-go"

# def resize_and_convert(image_path, size=(600, 450)):
#     """Resize and convert image to a supported format (PNG)."""
#     img = Image.open(image_path)
#     img = img.resize(size)
#     new_image_path = os.path.splitext(image_path)[0] + ".png"
#     img.save(new_image_path, "PNG")
#     return new_image_path

# def main():
#     """Shows basic usage of the Slides API.
#     Prints the number of slides and elements in a sample presentation.
#     """
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
#             creds = flow.run_local_server(port=8000)
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())

#     try:
#         service = build("slides", "v1", credentials=creds)
#         presentation = service.presentations().get(presentationId=PRESENTATION_ID).execute()
#         slides = presentation.get("slides")

#         if slides is None:
#             print("The presentation contains no slides.")
#         else:
#             print(f"The presentation contains {len(slides)} slides:")

#         # Create the title slide
#         title_slide_id = f"title_slide_{uuid.uuid4().hex}"
#         title_text_box_id = f"title_text_box_{uuid.uuid4().hex}"
#         requests = [
#             {
#                 "createSlide": {
#                     "objectId": title_slide_id,
#                     "insertionIndex": 0,
#                     "slideLayoutReference": {
#                         "predefinedLayout": "TITLE"
#                     }
#                 }
#             },
#             {
#                 "createShape": {
#                     "objectId": title_text_box_id,
#                     "shapeType": "TEXT_BOX",
#                     "elementProperties": {
#                         "pageObjectId": title_slide_id,
#                         "size": {
#                             "height": {
#                                 "magnitude": 1000000,
#                                 "unit": "EMU"
#                             },
#                             "width": {
#                                 "magnitude": 6000000,
#                                 "unit": "EMU"
#                             }
#                         },
#                         "transform": {
#                             "scaleX": 1,
#                             "scaleY": 1,
#                             "translateX": 1000000,
#                             "translateY": 1000000,
#                             "unit": "EMU"
#                         }
#                     }
#                 }
#             },
#             {
#                 "insertText": {
#                     "objectId": title_text_box_id,
#                     "text": presentation_text[0][0],
#                     "insertionIndex": 0,
#                 }
#             }
#         ]
#         service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

#         # Loop through presentation_text and create slides for each section
#         for i in range(1, len(presentation_text)):
#             section = presentation_text[i]
#             title = section[0]
#             bullets = section[1:]

#             slide_id = f"slide_{uuid.uuid4().hex}"  # Generate unique slide ID
#             title_box_id = f"title_box_{uuid.uuid4().hex}"  # Generate unique title box ID

#             # Create a slide for each section
#             requests = [
#                 {
#                     "createSlide": {
#                         "objectId": slide_id,
#                         "insertionIndex": i,
#                         "slideLayoutReference": {
#                             "predefinedLayout": "TITLE_AND_BODY"
#                         }
#                     }
#                 },
#                 {
#                     "createShape": {
#                         "objectId": title_box_id,
#                         "shapeType": "TEXT_BOX",
#                         "elementProperties": {
#                             "pageObjectId": slide_id,
#                             "size": {
#                                 "height": {
#                                     "magnitude": 1000000,
#                                     "unit": "EMU"
#                                 },
#                                 "width": {
#                                     "magnitude": 6000000,
#                                     "unit": "EMU"
#                                 }
#                             },
#                             "transform": {
#                                 "scaleX": 1,
#                                 "scaleY": 1,
#                                 "translateX": 1000000,
#                                 "translateY": 1000000,
#                                 "unit": "EMU"
#                             }
#                         }
#                     }
#                 },
#                 {
#                     "insertText": {
#                         "objectId": title_box_id,
#                         "text": title,
#                         "insertionIndex": 0,
#                     }
#                 }
#             ]

#             # Add bullet points
#             for j, bullet in enumerate(bullets):
#                 bullet_box_id = f"bullet_box_{uuid.uuid4().hex}"  # Generate unique bullet box ID
#                 requests.extend([
#                     {
#                         "createShape": {
#                             "objectId": bullet_box_id,
#                             "shapeType": "TEXT_BOX",
#                             "elementProperties": {
#                                 "pageObjectId": slide_id,
#                                 "size": {
#                                     "height": {
#                                         "magnitude": 1000000,
#                                         "unit": "EMU"
#                                     },
#                                     "width": {
#                                         "magnitude": 6000000,
#                                         "unit": "EMU"
#                                     }
#                                 },
#                                 "transform": {
#                                     "scaleX": 1,
#                                     "scaleY": 1,
#                                     "translateX": 1000000,
#                                     "translateY": 1000000 + j * 2000000,
#                                     "unit": "EMU"
#                                 }
#                             }
#                         }
#                     },
#                     {
#                         "insertText": {
#                             "objectId": bullet_box_id,
#                             "text": bullet,
#                             "insertionIndex": 0,
#                         }
#                     }
#                 ])

#             service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

#             # Upload image and add it to the slide
#             image_path = f"{i}.png"
#             if os.path.exists(image_path):
#                 image = resize_and_convert(image_path)
#                 drive_service = build("drive", "v3", credentials=creds)
#                 file_metadata = {
#                     "name": image,
#                     "mimeType": "image/png"
#                 }
#                 media = MediaFileUpload(image, mimetype="image/png", resumable=True)
#                 image_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
#                 drive_service.permissions().create(
#                     fileId=image_file['id'],
#                     body={
#                         'type': 'anyone',
#                         'role': 'reader',
#                     },
#                     fields='id',
#                 ).execute()

#                 image_id = f"image_{uuid.uuid4().hex}"  # Generate unique image ID

#                 requests.append({
#                     "createImage": {
#                         "objectId": image_id,
#                         "url": f"https://drive.google.com/uc?id={image_file['id']}",
#                         "elementProperties": {
#                             "pageObjectId": slide_id,
#                             "size": {
#                                 "height": {
#                                     "magnitude": 2812500,
#                                     "unit": "EMU"
#                                 },
#                                 "width": {
#                                     "magnitude": 3750000,
#                                     "unit": "EMU"
#                                 }
#                             },
#                             "transform": {
#                                 "scaleX": 1,
#                                 "scaleY": 1,
#                                 "translateX": 5297000,
#                                 "translateY": 1265625,
#                                 "unit": "EMU"
#                             }
#                         }
#                     }
#                 })
#                 service.presentations().batchUpdate(presentationId=PRESENTATION_ID, body={"requests": requests}).execute()

#         webbrowser.open(f"https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit")

#     except HttpError as err:
#         print(err)

# if __name__ == "__main__":
#     main()





# {
#                     "createImage": {
#                         "objectId": f"image{i}",
#                         "url": f"https://drive.google.com/uc?id={image_file['id']}",
#                         "elementProperties": {
#                             "pageObjectId": f"slide{i}",
#                             "size": {
#                                 "height": {
#                                     "magnitude": 2812500,
#                                     "unit": "EMU"
#                                 },
#                                 "width": {
#                                     "magnitude": 3750000,
#                                     "unit": "EMU"
#                                 }
#                             },
#                             "transform": {
#                                 "scaleX": 1,
#                                 "scaleY": 1,
#                                 "translateX": 5297000, 
#                                 "translateY": 1265625,
#                                 "unit": "EMU"
#                             }
#                         }
#                     }
#                 }