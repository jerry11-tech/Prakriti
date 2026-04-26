// =====================
// SCROLL ANIMATIONS
// =====================
var observer = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var el = entry.target;
      var anim = el.getAttribute('data-anim');
      el.classList.remove('animate-ready');
      el.classList.add('animate-' + anim);
      observer.unobserve(el);

      // Trigger dosha bars when demo panel enters view
      if (el.closest('#demo')) {
        setTimeout(function() {
          animateDoshaBars();
        }, 500);
      }
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.animate-ready').forEach(function(el) {
  observer.observe(el);
});

// =====================
// DOSHA BAR ANIMATION
// =====================
function animateDoshaBars() {
  var b1 = document.getElementById('b1');
  var b2 = document.getElementById('b2');
  var b3 = document.getElementById('b3');
  if (b1) b1.style.width = '62%';
  if (b2) b2.style.width = '25%';
  if (b3) b3.style.width = '13%';
}

// =====================
// QUESTIONNAIRE TOGGLE
// =====================
document.querySelectorAll('.q-opt').forEach(function(opt) {
  opt.addEventListener('click', function() {
    var siblings = this.parentElement.querySelectorAll('.q-opt');
    siblings.forEach(function(s) { s.classList.remove('sel'); });
    this.classList.add('sel');
  });
});

// =====================
// SMOOTH SCROLL FOR NAV LINKS
// =====================
document.querySelectorAll('a[href^="#"]').forEach(function(link) {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    var target = document.querySelector(this.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});

// =====================
// API INTEGRATION & AUTH
// =====================
document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = window.location.port === '3000' ? '' : (window.__PRAKRITI_API_URL || 'http://localhost:3000');
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const navLogin = document.getElementById('nav-login');
    
    if (navLogin) {
        if (token) {
            navLogin.textContent = role === 'admin' ? 'Admin' : 'Dashboard';
            navLogin.href = role === 'admin' ? 'admin.html' : 'dashboard.html';
        }
    }
    
    const analyzeBtn = document.querySelector('.btn-analyze');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            if (!token) {
                alert('Please login first to run an analysis!');
                window.location.href = 'login.html';
                return;
            }

            // ===== VALIDATE ANSWERS =====
            const qCards = document.querySelectorAll('.q-card');
            if (qCards.length < 3) {
                alert('Error: Questionnaire not found. Please refresh the page.');
                return;
            }

            const bodyFrameEl = qCards[0].querySelector('.sel');
            const skinTextureEl = qCards[1].querySelector('.sel');
            const sleepPatternEl = qCards[2].querySelector('.sel');

            if (!bodyFrameEl || !skinTextureEl || !sleepPatternEl) {
                alert('⚠️ Please answer ALL questions before analyzing');
                return;
            }

            const answers = {
                bodyFrame: bodyFrameEl.textContent,
                skinTexture: skinTextureEl.textContent,
                sleepPattern: sleepPatternEl.textContent
            };

            // ===== CREATE TEST IMAGE =====
            // For demo: Generate a simple test image from canvas
            // In production, replace with actual file upload input
            const canvas = document.createElement('canvas');
            canvas.width = 300;
            canvas.height = 300;
            const ctx = canvas.getContext('2d');

            // Draw a simple face outline
            ctx.fillStyle = '#FFD1A3'; // Skin tone
            ctx.fillRect(0, 0, 300, 300);
            ctx.fillStyle = '#8B4513'; // Face outline
            ctx.beginPath();
            ctx.arc(150, 150, 120, 0, Math.PI * 2);
            ctx.fill();

            // ===== SEND ANALYSIS REQUEST =====
            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;

            try {
                // Convert canvas to blob and create FormData
                canvas.toBlob(async (blob) => {
                    const formData = new FormData();
                    formData.append('image', blob, 'test_face.png');
                    formData.append('answers', JSON.stringify(answers));

                    console.log('[Frontend] Sending to /api/face/analyze...');
                    console.log('Answers:', answers);

                    const res = await fetch(`${apiBaseUrl}/api/face/analyze`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                            // NOTE: Don't set Content-Type! Browser will set it with boundary
                        },
                        body: formData
                    });

                    const data = await res.json();

                    if (!res.ok) {
                        // ===== ERROR HANDLING =====
                        console.error('Backend Error:', data);
                        const errorMsg = data.error || 'Unknown error';
                        const details = data.details || '';

                        let fullMsg = `❌ Analysis Failed\n\n${errorMsg}`;
                        if (details) fullMsg += `\n\nDetails: ${details}`;

                        alert(fullMsg);
                        analyzeBtn.textContent = 'Try Again';
                        analyzeBtn.disabled = false;
                        return;
                    }

                    // ===== SUCCESS =====
                    console.log('Analysis Result:', data);
                    analyzeBtn.textContent = 'Analysis Complete!';

                    // Extract prediction and confidence
                    const prediction = data.prediction || data.result?.prediction || 'Unknown';
                    const confidence = data.confidence || data.result?.confidence || 0;

                    // Update UI with results
                    const resultSpan = document.querySelector('.rstat-teal .rstat-val');
                    const confSpan = document.querySelector('.rstat-gold .rstat-val');
                    const domDosha = document.querySelector('.cond-val.grad');

                    if (resultSpan) resultSpan.textContent = prediction;
                    if (confSpan) confSpan.textContent = confidence + '%';
                    if (domDosha) domDosha.textContent = `${prediction} (${confidence}%)`;

                    alert(`✅ Success!\n\nPrakriti: ${prediction}\nConfidence: ${confidence}%`);

                    setTimeout(() => {
                        analyzeBtn.textContent = 'Analyze';
                        analyzeBtn.disabled = false;
                    }, 2000);
                });

            } catch(e) {
                console.error('Frontend Error:', e);
                alert(`❌ Connection Error\n\n${e.message}\n\nMake sure:\n1. Backend running on port 3000\n2. ML Service running on port 5000`);
                analyzeBtn.textContent = 'Try Again';
                analyzeBtn.disabled = false;
            }
        });
    }
});
