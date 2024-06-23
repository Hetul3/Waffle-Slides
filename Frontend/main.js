document.addEventListener('DOMContentLoaded', function() {
    const record_button = document.getElementById('record');
    let audioChunks = [];
    let rec;
    let isRecording = false;

    record_button.onclick = async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                rec = new MediaRecorder(stream);
                rec.ondataavailable = e => {
                    audioChunks.push(e.data);
                    if (rec.state === "inactive") {
                        uploadBlob()
                            .then(response => {
                                console.log(response);
                            })
                            .catch(error => {
                                console.error("Error uploading audio", error);
                            });
                        audioChunks = [];
                    }
                };

                console.log('Start recording');
                record_button.textContent = 'Stop';
                record_button.classList.add('record-clicked');
                audioChunks = [];
                rec.start();
                isRecording = true;
            } catch (error) {
                if (error.name === 'NotAllowedError') {
                    console.error('Permission to access microphone was denied');
                } else if (error.name === 'NotFoundError') {
                    console.error('No microphone was found');
                } else {
                    console.error('Error accessing audio stream:', error.message);
                }
            }
        } else {
            console.log('Stop recording');
            record_button.textContent = 'Record';
            record_button.classList.remove('record-clicked');
            rec.stop();
            isRecording = false;
        }
    };

    async function uploadBlob() {
        let audioBlob = new Blob(audioChunks, { type: 'audio/mpeg-3' });
        const formData = new FormData();
        formData.append('audio_data', audioBlob, 'file');
        formData.append('type', 'mp3');
      
        // Your server endpoint to upload audio:
        const apiUrl = "http://localhost:3000/upload/audio";
      
        const response = await fetch(apiUrl, {
          method: 'POST',
          cache: 'no-cache',
          body: formData
        });
        
        console.log("done");
        return response.json();
      }
});
