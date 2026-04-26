const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');
const store = require('../lib/store');
const { sendReportEmail, sendReportWithAttachment, sendWelcomeEmail } = require('../lib/email-service');

/**
 * Generate and download report
 */
router.post('/download', auth, async (req, res) => {
    try {
        const userId = req.user._id;
        const { format } = req.body || {};
        
        // Get user data
        const user = await store.getUserById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get all analyses for this user
        const analyses = await store.getAnalysisHistory(userId);
        
        // Generate report via Python ML service
        try {
            const reportFormat = format === 'text' ? 'text' : 'html';
            const endpoint = reportFormat === 'text' ? '/report/text' : '/report/html';
            
            const reportResponse = await fetch(`http://127.0.0.1:5000${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userName: user.name,
                    userEmail: user.email,
                    analyses: analyses
                })
            });

            if (!reportResponse.ok) {
                throw new Error('ML Service report generation failed');
            }
            
            const reportData = await reportResponse.json();
            
            if (!reportData.success) {
                throw new Error(reportData.error || 'Report generation failed');
            }
            
            // Set download headers
            const extension = reportFormat === 'text' ? 'txt' : 'html';
            const filename = `prakriti_report_${user.name.replace(/\s+/g, '_')}.${extension}`;
            
            res.setHeader('Content-Type', reportFormat === 'text' ? 'text/plain' : 'text/html');
            res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
            
            res.send(reportData.report);
            
        } catch (mlErr) {
            console.error('ML Service Error:', mlErr.message);
            res.status(500).json({ error: 'Failed to generate report' });
        }

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during report generation' });
    }
});

/**
 * Send report via email
 */
router.post('/email', auth, async (req, res) => {
    try {
        const userId = req.user._id;
        const { sendTo } = req.body || {};
        
        // Get user data
        const user = await store.getUserById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get all analyses for this user
        const analyses = await store.getAnalysisHistory(userId);
        
        // Generate report via Python ML service
        try {
            // Get both HTML and text versions
            const [htmlResponse, textResponse] = await Promise.all([
                fetch('http://127.0.0.1:5000/report/html', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userName: user.name,
                        userEmail: user.email,
                        analyses: analyses
                    })
                }),
                fetch('http://127.0.0.1:5000/report/text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userName: user.name,
                        userEmail: user.email,
                        analyses: analyses
                    })
                })
            ]);

            if (!htmlResponse.ok || !textResponse.ok) {
                throw new Error('ML Service report generation failed');
            }
            
            const htmlData = await htmlResponse.json();
            const textData = await textResponse.json();
            
            if (!htmlData.success || !textData.success) {
                throw new Error('Report generation failed');
            }
            
            // Send email
            const recipientEmail = sendTo || user.email;
            const emailResult = await sendReportWithAttachment(
                recipientEmail,
                user.name,
                `Your Prakriti AI Analysis Report - ${new Date().toLocaleDateString()}`,
                htmlData.report,
                textData.report,
                `prakriti_report_${user.name.replace(/\s+/g, '_')}.html`
            );
            
            if (!emailResult.success) {
                return res.status(500).json({ 
                    error: 'Failed to send email',
                    details: emailResult.error
                });
            }
            
            res.json({
                success: true,
                message: `Report sent successfully to ${recipientEmail}`,
                messageId: emailResult.messageId
            });
            
        } catch (mlErr) {
            console.error('ML Service Error:', mlErr.message);
            res.status(500).json({ error: 'Failed to generate report for email' });
        }

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during email send' });
    }
});

/**
 * Send report to multiple recipients
 */
router.post('/email/batch', auth, async (req, res) => {
    try {
        const userId = req.user._id;
        const { recipients } = req.body || {};
        
        if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
            return res.status(400).json({ error: 'No recipients specified' });
        }
        
        // Get user data
        const user = await store.getUserById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get all analyses for this user
        const analyses = await store.getAnalysisHistory(userId);
        
        // Generate report via Python ML service
        try {
            const htmlResponse = await fetch('http://127.0.0.1:5000/report/html', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userName: user.name,
                    userEmail: user.email,
                    analyses: analyses
                })
            });

            if (!htmlResponse.ok) {
                throw new Error('ML Service report generation failed');
            }
            
            const htmlData = await htmlResponse.json();
            
            if (!htmlData.success) {
                throw new Error('Report generation failed');
            }
            
            // Send to all recipients
            const results = [];
            for (const email of recipients) {
                const emailResult = await sendReportEmail(
                    email,
                    user.name,
                    `Your Prakriti AI Analysis Report - ${new Date().toLocaleDateString()}`,
                    htmlData.report,
                    htmlData.report
                );
                results.push({
                    email,
                    success: emailResult.success,
                    messageId: emailResult.messageId
                });
            }
            
            const successCount = results.filter(r => r.success).length;
            
            res.json({
                success: true,
                message: `Report sent to ${successCount}/${recipients.length} recipients`,
                results
            });
            
        } catch (mlErr) {
            console.error('ML Service Error:', mlErr.message);
            res.status(500).json({ error: 'Failed to generate report' });
        }

    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during batch email send' });
    }
});

/**
 * Test email service (send test email)
 */
router.post('/test-email', auth, async (req, res) => {
    try {
        const user = req.user;
        const { testEmail } = req.body || {};
        
        const recipientEmail = testEmail || user.email;
        
        const result = await sendWelcomeEmail(recipientEmail, user.name);
        
        if (!result.success) {
            return res.status(500).json({ 
                error: 'Failed to send test email',
                details: result.error
            });
        }
        
        res.json({
            success: true,
            message: `Test email sent to ${recipientEmail}`,
            messageId: result.messageId
        });
        
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during test email' });
    }
});

module.exports = router;
