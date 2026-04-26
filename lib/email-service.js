/**
 * Email Service for Prakriti AI
 * Sends analysis reports to users via email
 */

const nodemailer = require('nodemailer');
const fs = require('fs').promises;
const path = require('path');

// Configure email service
let transporter;

async function initializeEmailService() {
    // Get email configuration from environment
    const emailConfig = {
        service: process.env.EMAIL_SERVICE || 'gmail',
        auth: {
            user: process.env.EMAIL_USER || 'your-email@gmail.com',
            pass: process.env.EMAIL_PASSWORD || 'your-app-password'
        }
    };

    // For production, use environment variables or external service
    // For development/testing, use Ethereal (disposable email service)
    if (process.env.NODE_ENV === 'development' && !process.env.EMAIL_USER) {
        try {
            const testAccount = await nodemailer.createTestAccount();
            transporter = nodemailer.createTransport({
                host: testAccount.smtp.host,
                port: testAccount.smtp.port,
                secure: testAccount.smtp.secure,
                auth: {
                    user: testAccount.user,
                    pass: testAccount.pass
                }
            });
            console.log('✓ Email service initialized (test mode)');
            return testAccount;
        } catch (error) {
            console.log('Could not initialize test email account');
        }
    }

    // Use configured email service
    try {
        transporter = nodemailer.createTransport(emailConfig);
        // Verify connection
        await transporter.verify();
        console.log('✓ Email service initialized successfully');
        return true;
    } catch (error) {
        console.error('Email service initialization failed:', error.message);
        return false;
    }
}

/**
 * Send analysis report via email
 */
async function sendReportEmail(to, userName, subject, htmlContent, textContent) {
    if (!transporter) {
        console.error('Email service not initialized');
        return {
            success: false,
            error: 'Email service not available'
        };
    }

    try {
        const mailOptions = {
            from: process.env.EMAIL_FROM || `"Prakriti AI" <${process.env.EMAIL_USER || 'noreply@prakriti-ai.com'}>`,
            to: to,
            subject: subject || 'Your Prakriti AI Analysis Report',
            html: htmlContent,
            text: textContent,
            headers: {
                'X-Mailer': 'Prakriti AI System',
                'X-Priority': '1'
            }
        };

        const info = await transporter.sendMail(mailOptions);

        console.log(`✓ Email sent to ${to}`);
        
        // In test mode, log the preview URL
        if (info.messageId && process.env.NODE_ENV === 'development') {
            console.log(`Preview URL: ${nodemailer.getTestMessageUrl(info)}`);
        }

        return {
            success: true,
            messageId: info.messageId,
            response: info.response
        };

    } catch (error) {
        console.error('Error sending email:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Send report with HTML report as attachment
 */
async function sendReportWithAttachment(to, userName, subject, htmlContent, textContent, filename) {
    if (!transporter) {
        console.error('Email service not initialized');
        return {
            success: false,
            error: 'Email service not available'
        };
    }

    try {
        const mailOptions = {
            from: process.env.EMAIL_FROM || `"Prakriti AI" <${process.env.EMAIL_USER || 'noreply@prakriti-ai.com'}>`,
            to: to,
            subject: subject || 'Your Prakriti AI Analysis Report',
            html: `
                <p>Dear ${userName},</p>
                <p>Your personalized Prakriti AI analysis report is attached below.</p>
                <hr>
                ${htmlContent}
                <hr>
                <p>Best regards,<br>Prakriti AI Team</p>
            `,
            text: textContent
        };

        const info = await transporter.sendMail(mailOptions);

        console.log(`✓ Email sent to ${to} with attachment`);
        
        // In test mode, log the preview URL
        if (info.messageId && process.env.NODE_ENV === 'development') {
            console.log(`Preview URL: ${nodemailer.getTestMessageUrl(info)}`);
        }

        return {
            success: true,
            messageId: info.messageId,
            response: info.response
        };

    } catch (error) {
        console.error('Error sending email:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Send welcome email to new user
 */
async function sendWelcomeEmail(to, userName) {
    if (!transporter) {
        console.error('Email service not initialized');
        return {
            success: false,
            error: 'Email service not available'
        };
    }

    try {
        const mailOptions = {
            from: process.env.EMAIL_FROM || `"Prakriti AI" <${process.env.EMAIL_USER || 'noreply@prakriti-ai.com'}>`,
            to: to,
            subject: 'Welcome to Prakriti AI - Your Ayurvedic Journey Begins',
            html: `
                <!DOCTYPE html>
                <html>
                <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #3498db;">Welcome to Prakriti AI, ${userName}! 🧘</h1>
                        
                        <p>Thank you for joining our community dedicated to personalized Ayurvedic wellness analysis.</p>
                        
                        <h2 style="color: #2c3e50;">Getting Started</h2>
                        <ol>
                            <li>Complete your first Prakriti analysis questionnaire</li>
                            <li>Receive your personalized constitution profile (Vata, Pitta, or Kapha)</li>
                            <li>Get customized nutrition and lifestyle recommendations</li>
                            <li>Track your wellness journey with regular analyses</li>
                        </ol>
                        
                        <p>Take your analysis now: <a href="http://localhost:3000" style="color: #3498db;">Click here to get started</a></p>
                        
                        <hr>
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This is an automated message from Prakriti AI. Please do not reply to this email.
                        </p>
                    </div>
                </body>
                </html>
            `,
            text: `Welcome to Prakriti AI, ${userName}!\n\nThank you for joining our community. Visit http://localhost:3000 to start your analysis.`
        };

        const info = await transporter.sendMail(mailOptions);

        console.log(`✓ Welcome email sent to ${to}`);

        return {
            success: true,
            messageId: info.messageId
        };

    } catch (error) {
        console.error('Error sending welcome email:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

module.exports = {
    initializeEmailService,
    sendReportEmail,
    sendReportWithAttachment,
    sendWelcomeEmail
};
