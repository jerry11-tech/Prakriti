const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');
const store = require('../lib/store');

// Get personalized insights for a user
router.get('/insights', auth, async (req, res) => {
    try {
        const userId = req.user._id;
        
        // Get user data
        const user = await store.getUserById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get all analyses for this user
        const analyses = await store.getAnalysisHistory(userId);
        
        // Call Python ML service for insights
        try {
            const insightsResponse = await fetch('http://127.0.0.1:5000/insights', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userName: user.name,
                    userId: userId,
                    analyses: analyses
                })
            });

            if (!insightsResponse.ok) {
                throw new Error('ML Service insights failed');
            }
            
            const insightsData = await insightsResponse.json();
            res.json({
                success: true,
                insights: insightsData.data
            });
            
        } catch (mlErr) {
            console.error('ML Insights Error:', mlErr.message);
            // Fallback: generate basic insights without ML
            res.json({
                success: true,
                insights: {
                    user_name: user.name,
                    patterns: {
                        total_analyses: analyses.length,
                        primary_dosha: analyses.length > 0 ? analyses[0].prakritiResult : 'Not determined',
                        average_confidence: analyses.length > 0 ? 
                            Math.round(analyses.reduce((sum, a) => sum + a.confidence, 0) / analyses.length * 10) / 10 : 0
                    }
                }
            });
        }

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to generate insights' });
    }
});

// Get formatted insights report
router.get('/insights/report', auth, async (req, res) => {
    try {
        const userId = req.user._id;
        
        // Get user data
        const user = await store.getUserById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get all analyses for this user
        const analyses = await store.getAnalysisHistory(userId);
        
        // Call Python ML service for report
        try {
            const reportResponse = await fetch('http://127.0.0.1:5000/insights/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userName: user.name,
                    analyses: analyses
                })
            });

            if (!reportResponse.ok) {
                throw new Error('ML Service report failed');
            }
            
            const reportData = await reportResponse.json();
            res.json({
                success: true,
                report: reportData.report
            });
            
        } catch (mlErr) {
            console.error('ML Report Error:', mlErr.message);
            res.status(500).json({ error: 'Failed to generate report', fallback: true });
        }

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to retrieve report' });
    }
});

module.exports = router;
