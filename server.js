require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const store = require('./lib/store');
const axios = require('axios');
const multer = require('multer');

const app = express();
const PORT = process.env.PORT || 3000;

// Multer setup for handling file uploads via FormData
const storage = multer.memoryStorage();
const upload = multer({ 
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Standard API Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/analyse', require('./routes/analyse'));
app.use('/api/insights', require('./routes/insights'));
app.use('/api/admin', require('./routes/admin'));
app.use('/api/reports', require('./routes/reports'));

/**
 * New Face Analytics Integration Route
 * Handles multipart/form-data with an image file and questionnaire answers
 */
app.post('/api/face/analyze', upload.single('image'), async (req, res) => {
    try {
        const file = req.file;
        let answers = req.body.answers;

        // Validation
        if (!file) {
            return res.status(400).json({ error: "No image uploaded. Please capture or select a photo." });
        }

        if (!answers) {
            return res.status(400).json({ error: "No questionnaire answers provided." });
        }

        try {
            if (typeof answers === 'string') {
                answers = JSON.parse(answers);
            }
        } catch (e) {
            return res.status(400).json({ error: "Invalid questionnaire format." });
        }

        // Convert buffer to base64 for Python ML service (internal hop)
        const base64Image = `data:${file.mimetype};base64,${file.buffer.toString('base64')}`;

        console.log(`[Backend] Forwarding analysis request for ${file.originalname} (${file.size} bytes)`);

        // 1. Forward to ML Service Python Flask server running on 5000 for Visual Analysis
        let mlResponse;
        try {
            mlResponse = await axios.post(`${process.env.ML_SERVICE_URL || 'http://127.0.0.1:5000'}/analyze`, {
                image_base64: base64Image
            }, { timeout: 15000 });
        } catch (mlSvcErr) {
            console.error("ML Service Unreachable:", {
                message: mlSvcErr.message,
                code: mlSvcErr.code,
                errno: mlSvcErr.errno
            });

            // Provide specific troubleshooting for different error types
            let troubleShooting = "Ensure the Python Flask server is running on port 5000.";
            if (mlSvcErr.code === 'ECONNREFUSED') {
                troubleShooting = "Connection refused on port 5000. The ML Service is not running. Run: python ml_service/app.py";
            } else if (mlSvcErr.code === 'ETIMEDOUT') {
                troubleShooting = "Connection timed out. The ML Service may be overloaded or unresponsive.";
            }

            return res.status(503).json({
                error: "Facial Analysis Service is currently offline.",
                details: troubleShooting,
                errorCode: mlSvcErr.code
            });
        }

        const analysisData = mlResponse.data;
        if (analysisData.error) {
            console.error("ML Service Error Result:", analysisData.error);
            return res.status(400).json({ error: analysisData.error });
        }

        // 2. Get constitutional prediction based on visual features + lifestyle answers
        let predictionData = { prediction: 'Kapha', confidence: 85 };
        try {
            const predictResponse = await axios.post(`${process.env.ML_SERVICE_URL || 'http://127.0.0.1:5000'}/predict`, {
                answers: answers,
                faceShape: analysisData.face_shape
            }, { timeout: 5000 });
            
            if (predictResponse.data && predictResponse.data.prediction) {
                predictionData = predictResponse.data;
            }
        } catch (predErr) {
            console.warn("Prediction Model Error (falling back to default):", predErr.message);
        }

        // 3. Merge results and clean up
        const finalResult = {
            ...analysisData,
            prediction: predictionData.prediction,
            confidence: predictionData.confidence,
            timestamp: new Date().toISOString(),
            disclaimer: "AI-based estimation, not medical advice"
        };

        // 4. Persistence
        try {
            await store.createFaceAnalysis(finalResult);
        } catch (dbErr) {
            console.error("Database Save Error:", dbErr.message);
            // Don't fail the request if DB fails
        }

        res.json(finalResult);

    } catch (error) {
        console.error("Critical Analysis Failure:", error.stack);
        res.status(500).json({ 
            error: "Failed to process image analysis", 
            details: error.message 
        });
    }
});

// Fallback to index.html for unknown GETs (SPA support)
app.use((req, res) => {
    if (req.method === 'GET') {
        res.sendFile(path.join(__dirname, 'public', 'index.html'));
    } else {
        res.status(404).json({ error: "Not found" });
    }
});

// Start Database and Server
async function startServer() {
    try {
        await store.initStore();
        app.listen(PORT, () => {
            console.log(`============================================`);
            console.log(`Backend server running on http://localhost:${PORT}`);
            console.log(`Ready for Face & Prakriti Analysis`);
            console.log(`============================================`);
        });
    } catch (err) {
        console.error("Server Initialization Failed:", err);
    }
}

startServer();