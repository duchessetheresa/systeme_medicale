let stream = null;

function startCamera() {
    const webcamContainer = document.getElementById('webcam-container');
    const startCameraButton = document.getElementById('start-camera');
    const webcam = document.getElementById('webcam');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(mediaStream => {
            stream = mediaStream;
            webcam.srcObject = stream;
            webcamContainer.style.display = 'block';
            startCameraButton.style.display = 'none';
        })
        .catch(err => {
            document.getElementById('face-error').innerText = 'Erreur d\'accès à la caméra: ' + err;
            document.getElementById('face-error').style.display = 'block';
        });
}

function captureImage() {
    const webcam = document.getElementById('webcam');
    const canvas = document.createElement('canvas');
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    canvas.getContext('2d').drawImage(webcam, 0, 0, canvas.width, canvas.height);

    const imageDataUrl = canvas.toDataURL('image/jpeg');
    const preview = document.getElementById('preview');
    const capturedImage = document.getElementById('captured-image');
    const faceImageInput = document.getElementById('face_image');
    const submitBtn = document.getElementById('submit-btn');

    preview.src = imageDataUrl;
    capturedImage.style.display = 'block';

    // Convertir l'image en Blob pour l'envoyer via le formulaire
    fetch(imageDataUrl)
        .then(res => res.blob())
        .then(blob => {
            const file = new File([blob], 'face.jpg', { type: 'image/jpeg' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            faceImageInput.files = dataTransfer.files;
            submitBtn.disabled = false;
        });

    stopCamera();
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    const webcamContainer = document.getElementById('webcam-container');
    const startCameraButton = document.getElementById('start-camera');
    webcamContainer.style.display = 'none';
    startCameraButton.style.display = 'block';
}