"""
HTML & Text Report Generator for Prakriti AI
Generates comprehensive analysis reports in multiple formats
"""

import json
from datetime import datetime
from insights_generator import PrakritiInsights


class ReportGenerator:
    """Generate analysis reports in HTML and text formats"""
    
    def __init__(self):
        self.insights_gen = PrakritiInsights()
    
    def _generate_face_profile_html(self, insights: dict) -> str:
        """Generate HTML for face type profile"""
        face_analysis = insights.get('face_analysis', {})
        face_type = face_analysis.get('face_type', {})
        
        html = f"""
                <div class="profile-grid">
                    <div class="profile-item">
                        <strong>Face Shape:</strong> {face_type.get('face_type', 'Not specified')}
                    </div>
                    <div class="profile-item">
                        <strong>Skin Type:</strong> {face_type.get('skin', 'Not specified')}
                    </div>
                    <div class="profile-item">
                        <strong>Key Features:</strong> {face_type.get('features', 'Not specified')}
                    </div>
                    <div class="profile-item">
                        <strong>Complexion:</strong> {face_type.get('color', 'Not specified')}
                    </div>
                </div>
                <div class="profile-section">
                    <h4>Typical Concerns for Your Type:</h4>
                    <p>{face_type.get('typical_issues', 'None listed')}</p>
                </div>
        """
        return html
    
    def _generate_face_routine_html(self, insights: dict) -> str:
        """Generate HTML for face care routine"""
        face_analysis = insights.get('face_analysis', {})
        routine = face_analysis.get('face_care_routine', {})
        
        html = """
            <div class="routine-boxes">
        """
        
        # Morning routine
        if routine.get('morning'):
            html += """
                <div class="routine-box">
                    <h4>🌅 Morning Routine</h4>
                    <ul>
            """
            for item in routine.get('morning', []):
                html += f"                        <li>{item}</li>\n"
            html += """
                    </ul>
                </div>
            """
        
        # Evening routine
        if routine.get('evening'):
            html += """
                <div class="routine-box">
                    <h4>🌙 Evening Routine</h4>
                    <ul>
            """
            for item in routine.get('evening', []):
                html += f"                        <li>{item}</li>\n"
            html += """
                    </ul>
                </div>
            """
        
        # Weekly treatment
        if routine.get('weekly'):
            html += """
                <div class="routine-box">
                    <h4>📅 Weekly Treatment</h4>
                    <ul>
            """
            for item in routine.get('weekly', []):
                html += f"                        <li>{item}</li>\n"
            html += """
                    </ul>
                </div>
            """
        
        # Monthly treatment
        if routine.get('monthly'):
            html += """
                <div class="routine-box">
                    <h4>🎯 Monthly Deep Treatment</h4>
                    <ul>
            """
            for item in routine.get('monthly', []):
                html += f"                        <li>{item}</li>\n"
            html += """
                    </ul>
                </div>
            """
        
        html += """
            </div>
        """
        return html
    
    def generate_html_report(self, user_name: str, user_email: str, analyses: list, model_metrics: dict) -> str:
        """Generate a professional HTML report with model performance metrics"""
        
        insights = self.insights_gen.generate_personalized_insights(user_name, analyses)
        patterns = insights.get('patterns', {})
        recommendations = insights.get('personalized_recommendations', {})
        questionnaire = insights.get('questionnaire_insights', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prakriti AI - Personalized Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .metrics {{
            margin-top: 20px;
            padding: 10px;
            background: #e8f4f8;
            border-left: 5px solid #007acc;
        }}
        
        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .profile-item {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        
        .profile-item .label {{
            font-size: 12px;
            font-weight: 600;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        
        .profile-item .value {{
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 5px;
        }}
        
        .description {{
            background: #f0f3ff;
            padding: 15px;
            border-radius: 6px;
            line-height: 1.7;
            color: #34495e;
            margin-bottom: 15px;
        }}
        
        .warning-box {{
            background: #ffe6e6;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #e74c3c;
            color: #c0392b;
            margin-bottom: 15px;
        }}
        
        .recommendations-list {{
            list-style-position: inside;
            color: #34495e;
        }}
        
        .recommendations-list li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        .highlights {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .highlight-box .label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
        }}
        
        .highlight-box .value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .priority-actions {{
            background: #fffaf0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
        }}
        
        .priority-actions ol {{
            margin-left: 20px;
            color: #34495e;
        }}
        
        .priority-actions li {{
            margin: 10px 0;
            line-height: 1.6;
        }}
        
        .profile-box {{
            background: #f0f8ff;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .profile-item {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #d0e8f2;
            font-size: 14px;
        }}
        
        .profile-section {{
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #d0e8f2;
        }}
        
        .profile-section h4 {{
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .routine-boxes {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        
        .routine-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #bdc3c7;
        }}
        
        .routine-box h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        
        .routine-box ul {{
            list-style-position: inside;
            color: #34495e;
        }}
        
        .routine-box li {{
            margin: 8px 0;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
        
        .footer-logo {{
            font-size: 14px;
            font-weight: 600;
            color: #3498db;
            margin-bottom: 10px;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                padding: 20px;
                max-width: 100%;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
        
        @media (max-width: 768px) {{
            .profile-grid {{
                grid-template-columns: 1fr;
            }}
            .highlights {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🧘 Prakriti AI Analysis Report</h1>
            <p>Your Personalized Ayurvedic Constitution Profile</p>
            <p style="margin-top: 10px; font-size: 12px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- User Info -->
        <div class="user-info">
            <p><strong>Name:</strong> {user_name}</p>
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Total Analyses:</strong> {patterns.get('total_analyses', 0)}</p>
        </div>
        
        <!-- Constitution Profile -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">📊</span>
                <h2>Your Constitution Profile</h2>
            </div>
            <div class="highlights">
                <div class="highlight-box">
                    <div class="label">Primary Dosha</div>
                    <div class="value">{insights.get('primary_dosha', 'N/A')}</div>
                </div>
                <div class="highlight-box">
                    <div class="label">Confidence</div>
                    <div class="value">{patterns.get('average_confidence', 0)}%</div>
                </div>
                <div class="highlight-box">
                    <div class="label">Consistency</div>
                    <div class="value" style="font-size: 16px;">{patterns.get('consistency', 'N/A')}</div>
                </div>
            </div>
            <div class="profile-grid">
                <div class="profile-item">
                    <div class="label">Element</div>
                    <div class="value">{insights.get('dosha_element', 'N/A')}</div>
                </div>
                <div class="profile-item">
                    <div class="label">Body Type</div>
                    <div class="value">{questionnaire.get('latest_body_frame', 'N/A')}</div>
                </div>
                <div class="profile-item">
                    <div class="label">Skin Texture</div>
                    <div class="value">{questionnaire.get('latest_skin_texture', 'N/A')}</div>
                </div>
                <div class="profile-item">
                    <div class="label">Sleep Pattern</div>
                    <div class="value">{questionnaire.get('latest_sleep_pattern', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <!-- Characteristics -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">💫</span>
                <h2>Your Characteristics</h2>
            </div>
            <div class="description">
                {insights.get('characteristics', 'N/A')}
            </div>
        </div>
        
        <!-- Imbalance Warnings -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">⚠️</span>
                <h2>Signs of Imbalance</h2>
            </div>
            <div class="warning-box">
                {insights.get('imbalance_signs', 'N/A')}
            </div>
        </div>
        
        <!-- Nutrition Recommendations -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">🍽️</span>
                <h2>Nutrition Recommendations</h2>
            </div>
            <ul class="recommendations-list">
"""
        
        for rec in recommendations.get('nutrition', [])[:6]:
            html += f"                <li>{rec}</li>\n"
        
        html += """
            </ul>
        </div>
        
        <!-- Lifestyle Recommendations -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">🏃</span>
                <h2>Lifestyle Recommendations</h2>
            </div>
            <ul class="recommendations-list">
"""
        
        for rec in recommendations.get('lifestyle', [])[:6]:
            html += f"                <li>{rec}</li>\n"
        
        html += f"""
            </ul>
        </div>
        
        <!-- Daily Routine -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">⏰</span>
                <h2>Recommended Daily Routine</h2>
            </div>
            <div class="description">
                {recommendations.get('daily_routine', 'N/A')}
            </div>
        </div>
        
        <!-- Seasonal Adjustments -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">🌍</span>
                <h2>Seasonal Focus: {insights.get('current_season', 'N/A').title()}</h2>
            </div>
            <div class="description">
                <strong>Focus:</strong> {recommendations.get('seasonal_focus', 'N/A')}<br><br>
                <strong>Tips:</strong> {recommendations.get('seasonal_tips', 'N/A')}
            </div>
        </div>
        
        <!-- Priority Actions -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">🎯</span>
                <h2>Your Top Priority Actions</h2>
            </div>
            <div class="priority-actions">
                <ol>
"""
        
        for action in recommendations.get('priority_actions', []):
            html += f"                    <li>{action}</li>\n"
        
        html += f"""
                </ol>
            </div>
        </div>
        
        <!-- FACE ANALYSIS SECTION -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">👤</span>
                <h2>Your Face Type & Skin Profile</h2>
            </div>
            <div class="profile-box">
{self._generate_face_profile_html(insights)}
            </div>
        </div>
        
        <!-- FACE CARE ROUTINE SECTION -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">🧴</span>
                <h2>Your Personalized Face Care Routine</h2>
            </div>
{self._generate_face_routine_html(insights)}
        </div>
        
        <!-- Next Steps -->
        <div class="section">
            <div class="section-header">
                <span class="emoji">📅</span>
                <h2>Next Steps</h2>
            </div>
            <ul class="recommendations-list">
                <li>Review your priority actions and choose one to start this week</li>
                <li>Track your progress over 30 days and note any changes</li>
                <li>Take another Prakriti analysis in 2-3 months to monitor consistency</li>
                <li>Consider consulting with an Ayurvedic practitioner for personalized guidance</li>
                <li>Subscribe to our wellness newsletter for seasonal tips and updates</li>
            </ul>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-logo">Prakriti AI - Smart Ayurvedic Constitution Analysis</div>
            <p>This report is for educational purposes and should not replace professional medical advice.</p>
            <p>For personalized guidance, please consult a qualified Ayurvedic practitioner.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_text_report(self, user_name: str, user_email: str, analyses: list) -> str:
        """Generate a plain text report for email"""
        
        report = self.insights_gen.generate_summary_report(user_name, analyses)
        
        text = f"""
{'='*90}
PRAKRITI AI - PERSONALIZED ANALYSIS REPORT
{'='*90}

Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

USER INFORMATION
────────────────
Name: {user_name}
Email: {user_email}

{report}

NEXT STEPS
──────────
1. Review your priority actions and choose one to start this week
2. Track your progress over 30 days and note any changes
3. Take another Prakriti analysis in 2-3 months to monitor consistency
4. Consider consulting with an Ayurvedic practitioner for personalized guidance
5. Subscribe to our wellness newsletter for seasonal tips and updates

{'='*90}
This report is for educational purposes and should not replace professional medical advice.
For personalized guidance, please consult a qualified Ayurvedic practitioner.
{'='*90}
"""
        return text


def generate_report(user_name: str, user_email: str, analyses: list, format: str = 'html') -> str:
    """Main function to generate reports"""
    
    gen = ReportGenerator()
    
    if format == 'html':
        return gen.generate_html_report(user_name, user_email, analyses)
    elif format == 'text':
        return gen.generate_text_report(user_name, user_email, analyses)
    else:
        return gen.generate_text_report(user_name, user_email, analyses)
