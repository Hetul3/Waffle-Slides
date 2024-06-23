# Speech2SlAIdes

Frontend
- **HTML** interface with a button to record audio
- **JavaScript** handles the recording process and sends the audio file to the backend for processing.

Backend
- A **Flask** endpoint handle incoming audio files from the frontend.
- **Google Cloud Speech-to-Text API** converts the audio recordings into text with reliable speech recognition.
- **OpenAI's GPT** takes in converted text with a specially crafted prompt to organize the text into a structured format suitable for a presentation.
- For each slide, the LLM generates a keyword that represents the main idea of the slide
- **Unsplash API** searches and retrieves relevant images based on these keywords that represent main ideas
- The structured content (titles, bullet points, and images) is used to create a presentation using the **Google Slides API**
