document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('record');
    let audioChunks = [];
    let rec;
    let isRecording = false;

    recordButton.onclick = async () => {
        if (!isRecording) {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                rec = new MediaRecorder(stream);
                rec.ondataavailable = e => {
                    audioChunks.push(e.data);
                    if (rec.state === "inactive") {
                        let audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' });
                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'recording.mp3'); // Adjust the field name and filename as needed

                        // Your server endpoint to upload audio:
                        const apiUrl = "http://localhost:3000/upload";
                        // Before the fetch call
                        fetch(apiUrl, {
                            method: 'POST',
                            cache: 'no-cache',
                            body: formData
                        })
                        .then(response => {
                            if (!response.ok) {
                                console.log("here");
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            console.log("there");
                            return response.json();
                        })
                        .then(data => console.log(data))
                        .catch(error => console.error("Error uploading audio", error));

                        audioChunks = []; // Reset chunks for the next recording
                    }
                };

                console.log('Start recording');
                recordButton.textContent = 'Stop';
                recordButton.classList.add('record-clicked');
                audioChunks = [];
                rec.start();
                isRecording = true;
            } catch (error) {
                console.error("Error accessing the microphone", error);
            }
        } else {
            // Stop recording
            console.log('Stop recording');
            recordButton.textContent = 'Record';
            recordButton.classList.remove('record-clicked');
            rec.stop();
            isRecording = false;
            // Stop and release the media stream
            rec.stream.getTracks().forEach(track => track.stop());
        }
    };
});