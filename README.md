# Speech2SlAIdes

### Frontend
- **HTML** interface with a button to record audio
- **JavaScript** handles the recording process and sends the audio file to the backend for processing.

### Backend
- A **Flask** endpoint handle incoming audio files from the frontend.
- **Google Cloud Speech-to-Text API** converts the audio recordings into text with reliable speech recognition.
- **OpenAI's GPT** takes in converted text with a specially crafted prompt to organize the text into a structured format suitable for a presentation.
- For each slide, the LLM generates a keyword that represents the main idea of the slide
- **Unsplash API** searches and retrieves relevant images based on these keywords that represent main ideas
- The structured content (titles, bullet points, and images) is used to create a presentation using the **Google Slides API**

### How It works
The frontend, handles the recording process that creates a mp3 file of the recording that is handled by the Flask endpoint. Using Google Cloud Speech-to-Text API, the mp3 is converted to a textual transcript. OpenAI's GPT is methodically prompt-engineered to provide insightful bullet point summary, clustering titles and their associated bullet point together and seperating topics into different slides when it makes sense. An LLM agent using langchain reviews the title and bullet points in order create a search query for an associated image for the slide. The Unsplash API returns the associated image to the query. This information is stored locally and will be overriden by new queries. This information is preprocessed before being used for the Google Slides API from Google Cloud where it is formatted with the information. To get around image pasting, the locally stored images are resized to avoid large images, saved to a google drive using the Google Drive API from Google Cloud where it can then be used in the google slides. The slideshow is generated and is opened for the user.

**Youtube Link**: https://youtu.be/xShV5YMHvXg
