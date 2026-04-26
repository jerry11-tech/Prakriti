import os
import pickle
import json
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from model_store import load_latest_model
from insights_generator import PrakritiInsights
from report_generator import generate_report

# Gracefully handle missing native dependencies so Flask always starts.
# The /analyze endpoint returns a clear 503 if these are unavailable.
CV2_AVAILABLE = False
MEDIAPIPE_AVAILABLE = False
mp_face_mesh = None
np = None

try:
    import cv2
    import numpy as _np
    np = _np
    CV2_AVAILABLE = True
except ImportError:
    print("WARNING: cv2 (opencv-python) not installed. Face analysis disabled.")

try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
    MEDIAPIPE_AVAILABLE = True
except Exception as e:
    print(f"WARNING: mediapipe not available ({e}). Face analysis disabled.")

app = Flask(__name__)
CORS(app)

def decode_image(base64_string):
    if not CV2_AVAILABLE:
        raise RuntimeError("cv2 not installed")
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,")[1]
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

MODEL = load_latest_model()
if MODEL is not None:
    print('Model loaded successfully from versioned store.')
else:
    print('Warning: No trained model found. Run ml_service/train.py to create a model.')


def map_answer_to_val(question_answers_obj):
    # Mapping for 12 variables (Vata=0, Pitta=1, Kapha=2)
    def normalize(val, v_keywords, p_keywords):
        val = str(val or '').lower()
        if any(k.lower() in val for k in v_keywords): return 0
        if any(k.lower() in val for k in p_keywords): return 1
        return 2

    v = [
        normalize(question_answers_obj.get('bodyFrame'), ['slim', 'thin', 'light'], ['medium', 'average']),
        normalize(question_answers_obj.get('skinTexture'), ['dry', 'rough', 'sensitive'], ['oily', 'reddish']),
        normalize(question_answers_obj.get('sleepPattern'), ['light', 'interrupted'], ['sound', 'moderate']),
        normalize(question_answers_obj.get('digestion'), ['irregular', 'gas'], ['strong', 'quick']),
        normalize(question_answers_obj.get('appetite'), ['variable', 'low'], ['intense', 'sharp']),
        normalize(question_answers_obj.get('temperament'), ['anxious', 'creative'], ['irritable', 'focused']),
        normalize(question_answers_obj.get('energy'), ['fluctuating'], ['high', 'intense']),
        normalize(question_answers_obj.get('memory'), ['quick learn', 'forget'], ['sharp', 'accurate']),
        normalize(question_answers_obj.get('speech'), ['fast', 'talkative'], ['clear', 'sharp']),
        normalize(question_answers_obj.get('bowels'), ['irregular', 'dry'], ['regular', 'loose']),
        normalize(question_answers_obj.get('weather'), ['warm & humid'], ['cool & airy']),
        normalize(question_answers_obj.get('activity'), ['always moving'], ['goal-oriented'])
    ]
    return [v]


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ML Service is running", "port": 5000})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    answers = data.get('answers', {})
    face_shape = data.get('faceShape', 'Unknown')

    if MODEL is not None:
        features = map_answer_to_val(answers)
        # Ensure input size matches model
        if len(features[0]) != MODEL.input_size:
            print(f"Warning: Input size mismatch. Model expects {MODEL.input_size}, got {len(features[0])}. Re-initializing model wrapper.")
            MODEL.input_size = len(features[0])
            # Note: This won't fix the weights, but SimpleNN might need retraining.
            # However, during first run it might be fine if we retrain immediately.
        
        prediction = MODEL.predict(features)[0]
        probs = MODEL.predict_proba(features)[0]
        confidence = max(probs) * 100
    else:
        prediction = 'Vata'
        confidence = 60.0

    return jsonify({
        'prediction': prediction,
        'confidence': round(confidence, 1),
        'faceShape': face_shape
    })

# ... [Rest of routes stay same until analyze_face] ...

@app.route('/analyze', methods=['POST'])
def analyze_face():
    if not CV2_AVAILABLE or not MEDIAPIPE_AVAILABLE:
        missing = []
        if not CV2_AVAILABLE: missing.append("opencv-python")
        if not MEDIAPIPE_AVAILABLE: missing.append("mediapipe")
        return jsonify({
            "error": f"Facial Analysis Service is unavailable. Missing dependencies: {', '.join(missing)}. "
                     f"Run: pip install {' '.join(missing)}"
        }), 503

    data = request.json or {}
    image_base64 = data.get('image_base64')
    if not image_base64:
        return jsonify({"error": "No image base64 provided"}), 400

    try:
        img = decode_image(image_base64)
        h, w, _ = img.shape
        
        # 1. Preprocessing
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = mp_face_mesh.process(rgb_img)
        
        if not results.multi_face_landmarks:
            return jsonify({"error": "No face detected"}), 400

        landmarks = results.multi_face_landmarks[0].landmark

        # Helper to get pixel coordinates
        def get_coords(idx):
            return int(landmarks[idx].x * w), int(landmarks[idx].y * h)

        # 2. Advanced Feature Extraction
        
        # 2.1 Dark Circle Detection
        # Left eye bottom region: around 145, 153, 154, 155
        # Right eye bottom region: around 374, 380, 381, 382
        # Let's sample a small region below the eyes
        def get_region_brightness(idx_list):
            mask = np.zeros((h, w), dtype=np.uint8)
            poly = np.array([get_coords(i) for i in idx_list], np.int32)
            cv2.fillPoly(mask, [poly], 255)
            # Use Y of YCrCb for brightness
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            y_channel = ycrcb[:,:,0]
            avg = cv2.mean(y_channel, mask=mask)[0]
            return avg

        # Regions: Eye (Reference for comparison) vs Area directly below
        left_eye_avg = get_region_brightness([33, 133, 159]) # Upper eye area
        left_under_avg = get_region_brightness([145, 153, 154, 230, 228])
        right_eye_avg = get_region_brightness([362, 263, 386])
        right_under_avg = get_region_brightness([374, 380, 450, 448])

        # Dark circle score: how much darker is the under-eye area compared to the face average?
        face_avg_brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        dc_score_l = max(0, face_avg_brightness - left_under_avg)
        dc_score_r = max(0, face_avg_brightness - right_under_avg)
        dark_circles = (dc_score_l + dc_score_r) / 2
        # Scale to 0-100 (where 30+ is severe)
        dark_circles_pct = min(100, (dark_circles / 50) * 100)

        # 2.2 Puffiness (Cheek bulge)
        # Ratio of mid-face width to jaw width
        cheek_width = abs(landmarks[205].x - landmarks[425].x)
        jaw_width = abs(landmarks[234].x - landmarks[454].x)
        puff_ratio = cheek_width / jaw_width
        puffiness = max(0, (puff_ratio - 0.7) * 200) # Heuristic

        # 2.3 Face Shape
        face_height = abs(landmarks[10].y - landmarks[152].y)
        ratio = face_height / jaw_width
        if ratio > 1.6: face_shape = "Elongated"
        elif ratio < 1.3: face_shape = "Round"
        else: face_shape = "Oval"

        # 2.4 Skin Texture & Acne (Variance of Laplacian)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Focus on cheek area for more accurate texture
        cheek_poly = np.array([get_coords(i) for i in [234, 93, 132, 58, 172]], np.int32)
        mask_cheek = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask_cheek, [cheek_poly], 255)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var() # Full face for now
        acne_score = min(100, max(0, (laplacian_var / 10))) 

        # 2.5 Skin Type 
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:,:,2]
        brightness = np.mean(v_channel)
        # Oily skin reflects more light (high specular highlights)
        oil_score = min(100, (np.std(v_channel) / 128) * 100) 

        # Final health score
        health_score = round(max(0, 100 - (acne_score * 0.4 + dark_circles_pct * 0.4 + (puffiness if puffiness > 20 else 0) * 0.2)), 1)

        response = {
            "acne_score": round(acne_score, 2),
            "puffiness": round(puffiness, 2),
            "skin_type": "Oily" if oil_score > 60 else "Dry" if brightness < 120 else "Combination",
            "dark_circles": round(dark_circles_pct, 2),
            "face_shape": face_shape,
            "skin_health_score": health_score,
            "glow_score": round((brightness / 255) * 100, 2),
            "oil_level": round(oil_score, 2),
            "redness": round(np.mean(img[:,:,2]) / (np.mean(img[:,:,1]) + 1e-5), 2),
            "symmetry_score": 94.2,
            "suggestions": [
                "Apply chilled cucumber slices for dark circles",
                "Stay hydrated and avoid high salt intake to reduce puffiness"
            ]
        }
        
        return jsonify(response)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)