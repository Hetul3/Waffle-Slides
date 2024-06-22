document.addEventListener('DOMContentLoaded', function() {
    const record_button = document.getElementById('record');
    let audioChunks = [];
    let rec;
    let recordedAudio = new Audio();
    let isRecording = false;

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => { 
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
            }
        })
        .catch(error => {
            console.error('Error accessing audio stream:', error);
        });

    function sendData(data) {
        // Function to handle the data (e.g., send to server)
    }

    record_button.onclick = e => {
        if (!isRecording) {
            record_button.classList.add("record-clicked")
            record_button.textContent = 'Stop!';
            audioChunks = [];
            rec.start();
        } else {
            record_button.textContent = 'Record!';
            record_button.classList.remove("record-clicked")
            rec.stop();
        }
        isRecording = !isRecording;
    };
});
