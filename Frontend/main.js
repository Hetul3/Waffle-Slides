document.addEventListener('DOMContentLoaded', function() {
    const record_button = document.getElementById('record');
    let audioChunks = [];
    let rec;
    let recordedAudio = new Audio();
    let isRecording = false;

    record_button.onclick = async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                rec = new MediaRecorder(stream);
                rec.ondataavailable = e => {
                    audioChunks.push(e.data);
                    if (rec.state === "inactive") {
                        let blob = new Blob(audioChunks, { type: 'audio/mpeg-3' });
                        recordedAudio.src = URL.createObjectURL(blob);
                        recordedAudio.controls = true;
                        recordedAudio.autoplay = true;
                        sendData(blob);
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

    function sendData(data) {
        // Function to handle the data (e.g., send to server)
    }
});
