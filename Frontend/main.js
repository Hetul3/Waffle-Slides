document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('record');
    let audioChunks = [];
    let rec;
    let isRecording = false;

    recordButton.onclick = async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                rec = new MediaRecorder(stream);
                rec.ondataavailable = e => {
                    audioChunks.push(e.data);
                    if (rec.state === "inactive") {
                        saveRecording();
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
                recordButton.textContent = 'Stop';
                recordButton.classList.add('record-clicked');
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
            recordButton.textContent = 'Record';
            recordButton.classList.remove('record-clicked');
            rec.stop();
            isRecording = false;
        }
    };

    function saveRecording() {
        let blob = new Blob(audioChunks, { type: 'audio/mpeg' }); // Adjust the MIME type as needed
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'recording.mp3'; // Set the file name and extension
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    }

    async function uploadBlob() {
        let audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.mp3'); // Adjust the field name and filename as needed

        // Your server endpoint to upload audio:
        const apiUrl = "http://localhost:3000/upload";

        const response = await fetch(apiUrl, {
            method: 'POST',
            cache: 'no-cache',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }
});
