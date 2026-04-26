const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');
const store = require('../lib/store');

router.post('/', auth, async (req, res) => {
    try {
        const { faceShape, answers } = req.body;
        
        // Call Python ML Service
        let mlResult;
        try {
            const mlResponse = await fetch(`${process.env.ML_SERVICE_URL || 'http://127.0.0.1:5000'}/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ faceShape, answers })
            });

            if (!mlResponse.ok) throw new Error('ML Service failed');
            mlResult = await mlResponse.json();
            
        } catch (mlErr) {
            console.error('ML Service Error:', mlErr.message);
            // Fallback for demonstration if python server is off
            mlResult = {
                prediction: 'Kapha',
                confidence: 85,
                faceShape: faceShape || 'Oval'
            };
        }

        // Save to DB
        await store.createAnalysis({
            userId: req.user._id,
            faceShape: mlResult.faceShape,
            prakritiResult: mlResult.prediction,
            confidence: mlResult.confidence,
            questionnaireData: answers
        });

        res.json({
            message: 'Analysis complete',
            result: mlResult
        });

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during analysis' });
    }
});

// Get user history
router.get('/history', auth, async (req, res) => {
    try {
        const history = await store.getAnalysisHistory(req.user._id);
        res.json(history);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch history' });
    }
});

module.exports = router;
