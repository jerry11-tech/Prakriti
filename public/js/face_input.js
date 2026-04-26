document.addEventListener('DOMContentLoaded', () => {
    const btnUpload = document.getElementById('btn-upload');
    const btnCamera = document.getElementById('btn-camera');
    const btnCapture = document.getElementById('btn-capture');
    const fileInput = document.getElementById('file-input');
    const webcam = document.getElementById('webcam');
    const snapshot = document.getElementById('snapshot');
    const previewImage = document.getElementById('previewImage');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const analyzeBtn = document.querySelector('.btn-analyze');
    const errorDiv = document.getElementById('analysis-errors');

    let isCameraOn = false;
    let stream = null;
    let currentImageBlob = null;

    // Helper: Convert dataUrl to Blob
    function dataURLtoBlob(dataurl) {
        let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], {type:mime});
    }

    // Helper: Validity Check
    function checkFormValidity() {
        const qCards = document.querySelectorAll('.q-card');
        let allAnswered = true;
        qCards.forEach(card => {
            if (!card.querySelector('.sel')) {
                allAnswered = false;
            }
        });

        const hasImage = !!currentImageBlob;
        const currentAnalyzeBtn = document.querySelector('.btn-analyze');
        
        if (allAnswered && hasImage) {
            if (currentAnalyzeBtn) {
                currentAnalyzeBtn.disabled = false;
                currentAnalyzeBtn.title = 'Ready for analysis';
            }
            if (errorDiv) errorDiv.style.display = 'none';
        } else {
            if (currentAnalyzeBtn) {
                currentAnalyzeBtn.disabled = true;
                currentAnalyzeBtn.title = 'Please upload image and answer all questions';
            }
        }
    }

    // Listen for answer changes (they are handled in main.js but we add extra triggers here)
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('q-opt')) {
            setTimeout(checkFormValidity, 50); // Small delay to let selection happen
        }
    });

    btnUpload.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            currentImageBlob = file;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                showPreview(e.target.result);
                checkFormValidity();
            };
            reader.readAsDataURL(file);
        }
    });

    btnCamera.addEventListener('click', async () => {
        if (isCameraOn) {
            stopCamera();
        } else {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                webcam.srcObject = stream;
                webcam.style.display = 'block';
                uploadPlaceholder.style.display = 'none';
                previewImage.style.display = 'none';
                snapshot.style.display = 'none';
                btnCapture.style.display = 'block';
                btnCamera.innerHTML = '&#10006; Stop Camera';
                isCameraOn = true;
            } catch (err) {
                showError('Could not access camera. Please allow permissions.');
            }
        }
    });

    btnCapture.addEventListener('click', () => {
        if (!isCameraOn) return;
        snapshot.width = webcam.videoWidth;
        snapshot.height = webcam.videoHeight;
        const ctx = snapshot.getContext('2d');
        ctx.drawImage(webcam, 0, 0, snapshot.width, snapshot.height);
        
        const dataUrl = snapshot.toDataURL('image/jpeg', 0.9);
        currentImageBlob = dataURLtoBlob(dataUrl);
        
        showPreview(dataUrl);
        stopCamera();
        checkFormValidity();
    });

    function showPreview(dataUrl) {
        webcam.style.display = 'none';
        btnCapture.style.display = 'none';
        uploadPlaceholder.style.display = 'none';
        previewImage.src = dataUrl;
        previewImage.style.display = 'block';
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        webcam.style.display = 'none';
        btnCapture.style.display = 'none';
        btnCamera.innerHTML = '&#128247; Camera';
        isCameraOn = false;
    }

    function showError(msg) {
        if (errorDiv) {
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            alert(msg);
        }
    }

    if (analyzeBtn) {
        // Intercept analyze button to remove default listeners from main.js
        const newAnalyzeBtn = analyzeBtn.cloneNode(true);
        analyzeBtn.parentNode.replaceChild(newAnalyzeBtn, analyzeBtn);
        
        // Final listener on the fresh button
        newAnalyzeBtn.addEventListener('click', async () => {
            // Final Validation
            const qCards = document.querySelectorAll('.q-card');
            const unanswered = Array.from(qCards).filter(card => !card.querySelector('.sel'));
            
            if (unanswered.length > 0) {
                showError(`Please answer all ${qCards.length} questions before analyzing.`);
                return;
            }

            if (!currentImageBlob) {
                showError('Please upload an image or take a snapshot first.');
                return;
            }

            // Gather answers dynamically from all q-cards
            const answers = {};
            qCards.forEach(card => {
                const qName = card.getAttribute('data-question');
                const selectedOpt = card.querySelector('.sel');
                if (selectedOpt) {
                    answers[qName] = selectedOpt.textContent;
                }
            });

            const token = localStorage.getItem('token');
            const apiBaseUrl = window.location.port === '3000' ? '' : (window.__PRAKRITI_API_URL || 'http://localhost:3000');
            
            newAnalyzeBtn.innerHTML = '<span class="loader-spinner"></span> Analysing...';
            newAnalyzeBtn.disabled = true;
            if (errorDiv) errorDiv.style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('image', currentImageBlob, 'face.jpg');
                formData.append('answers', JSON.stringify(answers));

                const res = await fetch(`${apiBaseUrl}/api/face/analyze`, {
                    method: 'POST',
                    headers: {
                        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                    },
                    body: formData
                });

                const data = await res.json();
                if (res.ok) {
                    newAnalyzeBtn.textContent = 'Analysis Complete!';
                    populateUI(data);
                    
                    // Smooth scroll to results
                    document.querySelector('.rstat-teal').scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    showError(data.error || 'Failed to process image. Please try a clearer face photo.');
                    newAnalyzeBtn.textContent = 'Try Again';
                    newAnalyzeBtn.disabled = false;
                }
            } catch (e) {
                console.error(e);
                showError('Connection error. Please check if the server is running.');
                newAnalyzeBtn.textContent = 'Try Again';
                newAnalyzeBtn.disabled = false;
            }
        });
    }

    function populateUI(data) {
        // Face Shape
        const faceShapeEl = document.querySelector('.rstat-purple .rstat-val.p');
        if (faceShapeEl && data.face_shape) faceShapeEl.textContent = data.face_shape;

        // Detailed Conditions
        const darkCirclesEl = document.getElementById('dark_circles_val');
        if (darkCirclesEl) {
            const dc = data.dark_circles;
            darkCirclesEl.textContent = dc > 20 ? 'High' : dc > 10 ? 'Moderate' : 'Minimum';
            darkCirclesEl.style.color = dc > 20 ? '#ef4444' : dc > 10 ? '#fbbf24' : '#10b981';
        }

        const puffinessEl = document.getElementById('puffiness_val');
        if (puffinessEl) {
            puffinessEl.textContent = data.puffiness > 15 ? 'Puffy' : 'Normal';
            puffinessEl.style.color = data.puffiness > 15 ? '#fbbf24' : '#10b981';
        }

        const skinHealthEl = document.getElementById('skin_health_val');
        if (skinHealthEl) {
            skinHealthEl.textContent = data.skin_health_score + '%';
            skinHealthEl.style.color = data.skin_health_score > 80 ? '#10b981' : data.skin_health_score > 60 ? '#fbbf24' : '#ef4444';
        }

        const skinTypeEl = document.getElementById('skin_type_val');
        if (skinTypeEl) {
            skinTypeEl.textContent = data.skin_type;
        }
        
        // Dom Dosha Prediction Update
        if (data.prediction) {
            const resultSpan = document.querySelector('.rstat-teal .rstat-val');
            const confSpan = document.querySelector('.rstat-gold .rstat-val');
            const domDosha = document.querySelector('.cond-val.grad');
            
            if (resultSpan) resultSpan.textContent = data.prediction;
            if (confSpan) confSpan.textContent = data.confidence + '%';
            if (domDosha) domDosha.textContent = `${data.prediction} (${data.confidence}%)`;
            
            animateResultBars(data.prediction);
        }

        // Custom Success Alert
        const successMsg = document.createElement('div');
        successMsg.className = 'success-toast';
        successMsg.style.cssText = 'position:fixed; bottom:20px; right:20px; background:#10b981; color:white; padding:12px 20px; border-radius:8px; z-index:1000; box-shadow:0 10px 15px -3px rgba(0,0,0,0.1); animation: slideIn 0.3s ease-out;';
        successMsg.innerHTML = `&#10004; Analysis successful! Dominant: <b>${data.prediction}</b>`;
        document.body.appendChild(successMsg);
        setTimeout(() => successMsg.remove(), 4000);
    }

    function animateResultBars(dom) {
        const b1 = document.getElementById('b1');
        const b2 = document.getElementById('b2');
        const b3 = document.getElementById('b3');
        if (!b1) return;

        // Simple animation based on dominant
        if (dom === 'Kapha') {
            b1.style.width = '70%'; b2.style.width = '20%'; b3.style.width = '10%';
        } else if (dom === 'Pitta') {
            b1.style.width = '20%'; b2.style.width = '70%'; b3.style.width = '10%';
        } else {
            b1.style.width = '10%'; b2.style.width = '20%'; b3.style.width = '70%';
        }
    }
});
