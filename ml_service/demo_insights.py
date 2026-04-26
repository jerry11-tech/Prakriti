#!/usr/bin/env python3
"""
Prakriti AI - Personalized Insights Generator Demo
Generates sample personalized insights for all three dosha types
"""

import sys
sys.path.insert(0, r'c:\Users\dhira\Downloads\prakriti-ai-ready-deploy')

from insights_generator import PrakritiInsights
from datetime import datetime, timedelta

# Sample data for different users
SAMPLE_USERS = {
    'Vata': {
        'name': 'Rahul Kumar',
        'analyses': [
            {
                'userId': 'user-001',
                'faceShape': 'Rectangular',
                'prakritiResult': 'Vata',
                'confidence': 87.3,
                'questionnaireData': {
                    'bodyFrame': 'slim',
                    'skinTexture': 'dry',
                    'sleepPattern': 'light'
                },
                'timestamp': (datetime.now() - timedelta(days=5)).isoformat()
            },
            {
                'userId': 'user-001',
                'faceShape': 'Rectangular',
                'prakritiResult': 'Vata',
                'confidence': 84.5,
                'questionnaireData': {
                    'bodyFrame': 'thin',
                    'skinTexture': 'sensitive',
                    'sleepPattern': 'irregular'
                },
                'timestamp': (datetime.now() - timedelta(days=2)).isoformat()
            }
        ]
    },
    'Pitta': {
        'name': 'Priya Sharma',
        'analyses': [
            {
                'userId': 'user-002',
                'faceShape': 'Oval',
                'prakritiResult': 'Pitta',
                'confidence': 92.1,
                'questionnaireData': {
                    'bodyFrame': 'medium',
                    'skinTexture': 'oily',
                    'sleepPattern': 'regular'
                },
                'timestamp': (datetime.now() - timedelta(days=7)).isoformat()
            },
            {
                'userId': 'user-002',
                'faceShape': 'Heart',
                'prakritiResult': 'Pitta',
                'confidence': 89.7,
                'questionnaireData': {
                    'bodyFrame': 'medium',
                    'skinTexture': 'smooth',
                    'sleepPattern': 'moderate'
                },
                'timestamp': (datetime.now() - timedelta(days=3)).isoformat()
            }
        ]
    },
    'Kapha': {
        'name': 'Amit Patel',
        'analyses': [
            {
                'userId': 'user-003',
                'faceShape': 'Round',
                'prakritiResult': 'Kapha',
                'confidence': 88.9,
                'questionnaireData': {
                    'bodyFrame': 'large',
                    'skinTexture': 'smooth',
                    'sleepPattern': 'heavy'
                },
                'timestamp': (datetime.now() - timedelta(days=10)).isoformat()
            },
            {
                'userId': 'user-003',
                'faceShape': 'Round',
                'prakritiResult': 'Kapha',
                'confidence': 86.4,
                'questionnaireData': {
                    'bodyFrame': 'solid',
                    'skinTexture': 'smooth',
                    'sleepPattern': 'deep'
                },
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
            }
        ]
    }
}

def generate_demo_insights():
    """Generate and display personalized insights for all dosha types"""
    
    insights_gen = PrakritiInsights()
    
    print("\n" + "="*90)
    print(" "*20 + "PRAKRITI AI - PERSONALIZED INSIGHTS DEMO")
    print("="*90 + "\n")
    
    for dosha_type, user_data in SAMPLE_USERS.items():
        user_name = user_data['name']
        analyses = user_data['analyses']
        
        print(f"\n{'='*90}")
        print(f"USER: {user_name.upper()} ({dosha_type})")
        print(f"{'='*90}\n")
        
        # Generate report
        report = insights_gen.generate_summary_report(user_name, analyses)
        print(report)
        
        # Generate JSON insights
        insights = insights_gen.generate_personalized_insights(user_name, analyses)
        
        print("\n📋 STRUCTURED INSIGHTS DATA:")
        print(f"   - Total Analyses: {insights['patterns']['total_analyses']}")
        print(f"   - Average Confidence: {insights['patterns']['average_confidence']}%")
        print(f"   - Consistency: {insights['patterns']['consistency']}")
        print(f"   - Dosha Distribution: {insights['patterns']['dosha_distribution']}")
        
        print("\n🎯 PRIORITY ACTIONS:")
        for i, action in enumerate(insights.get('personalized_recommendations', {}).get('priority_actions', []), 1):
            print(f"   {i}. {action}")
        
        print("\n" + "-"*90 + "\n")

if __name__ == '__main__':
    generate_demo_insights()
    
    print("\n✅ Demo completed successfully!")
    print("\nThese insights can be:")
    print("  1. Displayed on the user dashboard")
    print("  2. Downloaded as a full report")
    print("  3. Accessed via the API endpoints:")
    print("     - GET /api/insights/insights")
    print("     - GET /api/insights/insights/report")
    print("\n" + "="*90 + "\n")
