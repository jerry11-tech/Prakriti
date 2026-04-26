"""
Personalized Insights Generator for Prakriti AI
Analyzes user data and generates customized ayurvedic recommendations
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from model_store import load_latest_model


class PrakritiInsights:
    """Generate personalized insights based on prakriti type and user patterns"""
    
    # Face Concern Analysis Database
    FACE_CONCERNS_DATABASE = {
        'acne': {
            'Vata': {
                'cause': 'Irregular skincare routine and dry skin',
                'tips': [
                    'Use warm oil-based face wash (sesame or almond oil)',
                    'Apply warm compresses to affected areas',
                    'Avoid harsh scrubbing; use gentle circular motions',
                    'Drink plenty of warm water with ginger',
                    'Avoid excessive caffeine and cold drinks',
                    'Sleep 8 hours regularly to reduce stress'
                ]
            },
            'Pitta': {
                'cause': 'Excess heat and inflammation in skin',
                'tips': [
                    'Use cooling face masks (neem, turmeric, sandalwood)',
                    'Avoid hot water; use lukewarm or cool water',
                    'Apply rose water or aloe vera gel daily',
                    'Reduce spicy, fried, and salty foods',
                    'Drink coconut water and herbal teas (chamomile, mint)',
                    'Avoid sun exposure during peak hours (10am-4pm)',
                    'Practice cooling pranayama (Sitali breath) in morning'
                ]
            },
            'Kapha': {
                'cause': 'Excess oil and congestion',
                'tips': [
                    'Use light, oil-control face wash',
                    'Apply turmeric and honey mask 2x weekly',
                    'Use warm water and washcloth for gentle exfoliation',
                    'Reduce dairy, oily, and heavy foods',
                    'Exercise 4-5 times weekly to stimulate circulation',
                    'Use dry brushing (garshana) on face and body',
                    'Start day with lemon water to cleanse system'
                ]
            }
        },
        'dullness': {
            'Vata': {
                'cause': 'Poor circulation and dehydration',
                'tips': [
                    'Daily facial oil massage (abhyanga) for 5 minutes',
                    'Use face masks with sesame oil and turmeric',
                    'Increase warm, nourishing foods',
                    'Practice facial marma point massage',
                    'Stay well hydrated with warm herbal teas',
                    'Get adequate sleep (10-11pm bedtime)'
                ]
            },
            'Pitta': {
                'cause': 'Excess heat damaging skin radiance',
                'tips': [
                    'Weekly facial with cooling ingredients (rose, sandal)',
                    'Reduce hot spices and inflammatory foods',
                    'Drink plenty of cooling herbal teas',
                    'Use vitamin C serums and antioxidants',
                    'Practice evening pranayama for cooling effect',
                    'Ensure 7-8 hours quality sleep'
                ]
            },
            'Kapha': {
                'cause': 'Sluggish metabolism affecting skin clarity',
                'tips': [
                    'Weekly dry brushing followed by light oil',
                    'Use brightening masks (turmeric, honey, lemon)',
                    'Increase physical activity to boost circulation',
                    'Consume warming spices daily',
                    'Early morning sun exposure for vitamin D',
                    'Reduce sugar and refined carbs'
                ]
            }
        },
        'oiliness': {
            'Vata': {
                'cause': 'Irregular skincare routine',
                'tips': [
                    'Use consistent oil massage routine to balance',
                    'Light sesame oil 2-3 times weekly',
                    'Avoid harsh drying products',
                    'Balance routine with consistent bedtime'
                ]
            },
            'Pitta': {
                'cause': 'Excess heat increasing sebum production',
                'tips': [
                    'Use rose water and neem-based products',
                    'Clay masks (white or green) 2x weekly',
                    'Reduce spicy, fried foods and alcohol',
                    'Stay hydrated with cooling beverages',
                    'Avoid touching face throughout day'
                ]
            },
            'Kapha': {
                'cause': 'Heavy, oily constitution',
                'tips': [
                    'Turmeric and gram flour masks 2x weekly',
                    'Dry brushing to improve circulation',
                    'Reduce dairy and oil consumption',
                    'Daily exercise to stimulate metabolism',
                    'Limit heavy creams; use lightweight lotions'
                ]
            }
        },
        'wrinkles': {
            'Vata': {
                'cause': 'Dry skin and poor circulation',
                'tips': [
                    'Daily facial oil massage with sesame oil',
                    'Use hydrating face masks with honey',
                    'Drink warm herbal teas (ashwagandha)',
                    'Increase healthy fats in diet',
                    'Practice facial yoga for skin elasticity'
                ]
            },
            'Pitta': {
                'cause': 'Sun damage and excess heat',
                'tips': [
                    'Use SPF 30+ daily sunscreen',
                    'Apply cooling hydrating serums',
                    'Increase antioxidant-rich foods',
                    'Use aloe vera and rose water regularly',
                    'Reduce sun exposure especially 10am-4pm'
                ]
            },
            'Kapha': {
                'cause': 'Sluggish skin renewal',
                'tips': [
                    'Exfoliate 2x weekly with gentle scrubs',
                    'Use retinol or vitamin A products',
                    'Increase warming herbs (ginger, turmeric)',
                    'Daily exercise to boost circulation',
                    'Reduce heavy dairy products'
                ]
            }
        },
        'puffiness': {
            'Vata': {
                'cause': 'Irregular sleep and poor circulation',
                'tips': [
                    'Maintain consistent 10-11pm sleep schedule',
                    'Massage face with warm sesame oil in morning',
                    'Use ginger tea to improve circulation',
                    'Elevate head while sleeping'
                ]
            },
            'Pitta': {
                'cause': 'Excess heat and inflammation',
                'tips': [
                    'Cold water facial rinse in morning',
                    'Use cooling eye masks (rose water, cucumber)',
                    'Reduce salt intake',
                    'Drink plenty of water',
                    'Apply turmeric face packs for anti-inflammatory'
                ]
            },
            'Kapha': {
                'cause': 'Water retention and sluggish lymph',
                'tips': [
                    'Facial lymphatic drainage massage',
                    'Warm water rinse followed by facial exercise',
                    'Reduce salt and processed foods',
                    'Morning cardio to stimulate circulation',
                    'Use turmeric and ginger to reduce water retention'
                ]
            }
        },
        'dark_circles': {
            'Vata': {
                'cause': 'Sleep irregularity and stress',
                'tips': [
                    'Establish 10-11pm bedtime routine',
                    'Use warm oil massage before bed',
                    'Drink warm milk with ghee at night',
                    'Practice meditation to reduce stress',
                    'Apply sesame oil under eyes at night'
                ]
            },
            'Pitta': {
                'cause': 'Excess heat and overwork',
                'tips': [
                    'Cool compress with rose water or chamomile',
                    'Reduce workload and take regular breaks',
                    'Apply aloe vera under eyes',
                    'Drink cooling herbal teas',
                    'Get 8 hours quality sleep'
                ]
            },
            'Kapha': {
                'cause': 'Poor circulation and fluid retention',
                'tips': [
                    'Morning facial massage to improve circulation',
                    'Use turmeric and honey under eye masks',
                    'Daily cardio exercise',
                    'Reduce heavy foods and dairy',
                    'Keep head elevated while sleeping'
                ]
            }
        }
    }
    
    # Prakriti-specific recommendations
    PRAKRITI_GUIDANCE = {
        'Vata': {
            'element': 'Air & Ether',
            'characteristics': 'Creative, energetic, enthusiastic, quick-thinking',
            'imbalance_signs': 'Anxiety, dry skin, irregular digestion, restlessness',
            'nutrition': [
                'Warm, cooked foods with good fats (ghee, oils)',
                'Sweet, sour, and salty tastes (minimize bitter, astringent)',
                'Grounding spices: ginger, cumin, black pepper',
                'Avoid cold, raw, and light foods'
            ],
            'lifestyle': [
                'Maintain consistent daily routine (sleep/wake times)',
                'Regular oil massage (abhyanga) - grounding practice',
                'Gentle, grounding exercise (yoga, walking, tai chi)',
                'Avoid excessive travel and stimulation',
                'Keep warm clothing and environment'
            ],
            'daily_routine': 'Wake 6-7am, sleep 10-11pm, practice meditation'
        },
        'Pitta': {
            'element': 'Fire & Water',
            'characteristics': 'Focused, intelligent, competitive, ambitious',
            'imbalance_signs': 'Inflammation, acid reflux, anger, skin issues',
            'nutrition': [
                'Cooling foods: coconut, cucumber, leafy greens',
                'Sweet, bitter, astringent tastes (minimize sour, salty)',
                'Cooling spices: coriander, cumin, fennel',
                'Avoid spicy, fried, and heavy foods'
            ],
            'lifestyle': [
                'Cooling practices: moon gazing, water activities',
                'Moderate exercise during cooler times (morning/evening)',
                'Meditation and pranayama for emotional balance',
                'Limit competitive/stressful situations',
                'Maintain cool environment'
            ],
            'daily_routine': 'Wake 5-6am, sleep 10-11pm, balance work with rest'
        },
        'Kapha': {
            'element': 'Water & Earth',
            'characteristics': 'Stable, calm, compassionate, loyal',
            'imbalance_signs': 'Weight gain, sluggishness, congestion, depression',
            'nutrition': [
                'Light, warm, stimulating foods',
                'Pungent, bitter, astringent tastes (minimize sweet, oily)',
                'Warming spices: black pepper, ginger, cinnamon',
                'Favor fresh, cooked vegetables and legumes'
            ],
            'lifestyle': [
                'Stimulating exercise: cardio, dancing, brisk walking',
                'Dry massage (garshana) to stimulate circulation',
                'Morning sun exposure and activities',
                'Mental stimulation and social engagement',
                'Warm, dry environment'
            ],
            'daily_routine': 'Wake 5-6am early, sleep 9-10pm, stay active'
        }
    }
    
    SEASONAL_ADJUSTMENTS = {
        'spring': {
            'focus': 'Kapha balancing',
            'tips': 'Increase warm spices, do detoxification, active exercise'
        },
        'summer': {
            'focus': 'Pitta balancing',
            'tips': 'Stay hydrated, favor cooling foods, protect from heat'
        },
        'autumn': {
            'focus': 'Vata balancing',
            'tips': 'Warm oils, consistent routine, comfort foods'
        },
        'winter': {
            'focus': 'Vata & Kapha balancing',
            'tips': 'Stay warm, warming foods, maintain movement'
        }
    }
    
    def __init__(self):
        self.model = load_latest_model()
    
    def get_current_season(self) -> str:
        """Determine current season"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def analyze_patterns(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Analyze user's analysis history for patterns"""
        if not analyses:
            return {
                'total_analyses': 0,
                'primary_dosha': None,
                'dosha_distribution': {},
                'average_confidence': 0,
                'consistency': 'New user'
            }
        
        prakriti_counts = {}
        confidences = []
        
        for analysis in analyses:
            prakriti = analysis.get('prakritiResult', 'Unknown')
            prakriti_counts[prakriti] = prakriti_counts.get(prakriti, 0) + 1
            confidences.append(analysis.get('confidence', 0))
        
        primary_dosha = max(prakriti_counts, key=prakriti_counts.get) if prakriti_counts else None
        primary_count = prakriti_counts.get(primary_dosha, 0)
        total = len(analyses)
        consistency = 'Very Consistent' if primary_count >= total * 0.8 else 'Somewhat Variable' if primary_count >= total * 0.6 else 'Highly Variable'
        
        return {
            'total_analyses': total,
            'primary_dosha': primary_dosha,
            'dosha_distribution': prakriti_counts,
            'average_confidence': round(sum(confidences) / len(confidences), 1) if confidences else 0,
            'consistency': consistency
        }
    
    def extract_questionnaire_insights(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Extract patterns from questionnaire responses"""
        if not analyses:
            return {}
        
        latest = analyses[-1] if analyses else {}
        questionnaire = latest.get('questionnaireData', {})
        
        return {
            'latest_body_frame': questionnaire.get('bodyFrame', 'Not specified'),
            'latest_skin_texture': questionnaire.get('skinTexture', 'Not specified'),
            'latest_sleep_pattern': questionnaire.get('sleepPattern', 'Not specified'),
            'face_shape': latest.get('faceShape', 'Not specified')
        }
    
    def analyze_face_concerns(self, analyses: List[Dict], dosha: str) -> Dict[str, Any]:
        """Analyze face concerns and generate personalized skincare recommendations"""
        if not analyses:
            return {'concerns': [], 'recommendations': []}
        
        latest = analyses[-1] if analyses else {}
        questionnaire = latest.get('questionnaireData', {})
        
        # Extract face concerns from questionnaire
        face_concerns = []
        if questionnaire.get('skinCondition'):
            face_concerns.append(questionnaire.get('skinCondition'))
        if questionnaire.get('faceConcerns'):
            if isinstance(questionnaire.get('faceConcerns'), list):
                face_concerns.extend(questionnaire.get('faceConcerns'))
            else:
                face_concerns.append(questionnaire.get('faceConcerns'))
        
        # Generate recommendations based on concerns and dosha
        recommendations = []
        for concern in face_concerns:
            concern_lower = concern.lower() if concern else ''
            
            # Match concern to database
            for db_concern, db_doshas in self.FACE_CONCERNS_DATABASE.items():
                if db_concern in concern_lower or concern_lower in db_concern:
                    if dosha in db_doshas:
                        recommendations.append({
                            'concern': concern,
                            'cause': db_doshas[dosha]['cause'],
                            'tips': db_doshas[dosha]['tips']
                        })
                    break
        
        # If no specific concerns, provide general face health tips based on skin texture
        if not recommendations:
            skin_texture = questionnaire.get('skinTexture', 'normal').lower()
            
            if 'oily' in skin_texture:
                recommendations.append({
                    'concern': 'General oily skin',
                    'cause': 'Natural skin condition',
                    'tips': self.FACE_CONCERNS_DATABASE.get('oiliness', {}).get(dosha, {}).get('tips', [])
                })
            elif 'dry' in skin_texture:
                recommendations.append({
                    'concern': 'General dry skin',
                    'cause': 'Natural skin condition',
                    'tips': self.FACE_CONCERNS_DATABASE.get('dullness', {}).get(dosha, {}).get('tips', [])
                })
        
        return {
            'concerns': face_concerns,
            'recommendations': recommendations,
            'skin_texture': questionnaire.get('skinTexture', 'Not specified'),
            'face_shape': latest.get('faceShape', 'Not specified')
        }
    
    def generate_dosha_face_type(self, dosha: str, face_shape: str) -> Dict[str, str]:
        """Describe face characteristics based on dosha"""
        face_characteristics = {
            'Vata': {
                'face_type': 'Angular, elongated face',
                'skin': 'Thin, dry, cool to touch',
                'features': 'Fine features, prominent bone structure',
                'typical_issues': 'Fine lines, dry patches, sensitivity',
                'color': 'Dusky, matte complexion'
            },
            'Pitta': {
                'face_type': 'Moderate, heart or square shaped face',
                'skin': 'Fair, warm, oily in T-zone',
                'features': 'Sharp features, moderate frame',
                'typical_issues': 'Acne, redness, sensitivity to sun',
                'color': 'Reddish, warm complexion'
            },
            'Kapha': {
                'face_type': 'Round, full, square-shaped face',
                'skin': 'Thick, oily, smooth, cool to touch',
                'features': 'Soft features, fuller frame',
                'typical_issues': 'Clogged pores, oiliness, puffiness',
                'color': 'Fair, pale complexion'
            }
        }
        
        return face_characteristics.get(dosha, {
            'face_type': 'Unique individual features',
            'skin': 'Individual skin type',
            'features': 'Unique to your constitution',
            'typical_issues': 'Personalized recommendations below',
            'color': 'Individual complexion'
        })
    
    def generate_face_care_routine(self, dosha: str) -> Dict[str, Any]:
        """Generate a complete face care routine for the dosha"""
        routines = {
            'Vata': {
                'morning': [
                    'Rinse face with warm water',
                    'Apply warm sesame or almond oil gently',
                    'Follow with warm milk-based face cream',
                    'Drink warm herbal tea (ginger, ashwagandha)'
                ],
                'evening': [
                    'Cleanse with warm oil-based cleanser',
                    'Apply warm compresses to face',
                    'Use rose water or herbal toner',
                    'Apply nourishing night oil (sesame, brahmi)'
                ],
                'weekly': [
                    'Oil massage (abhyanga) on face and scalp - 15 mins',
                    'Warm milk and honey mask - 20 mins',
                    'Gentle facial massage with oils'
                ],
                'monthly': [
                    'Deep tissue facial massage',
                    'Specialized Ayurvedic facial treatment'
                ]
            },
            'Pitta': {
                'morning': [
                    'Rinse face with cool water',
                    'Apply cooling rose water',
                    'Use lightweight aloe vera gel',
                    'Drink cooling herbal tea (chamomile, rose)'
                ],
                'evening': [
                    'Cleanse with gentle, cooling cleanser',
                    'Apply sandalwood face wash',
                    'Spray rose water liberally',
                    'Use cooling moisturizer or aloe vera'
                ],
                'weekly': [
                    'Turmeric and neem mask - 15 mins',
                    'Sandalwood and coconut oil massage',
                    'Cool water facial spray'
                ],
                'monthly': [
                    'Professional cooling facial',
                    'Herbal steam with cooling herbs'
                ]
            },
            'Kapha': {
                'morning': [
                    'Rinse face with warm water',
                    'Use turmeric and honey cleanser',
                    'Apply stimulating face pack (ginger, turmeric)',
                    'Drink warming herbal tea (ginger, black pepper)'
                ],
                'evening': [
                    'Cleanse with gram flour and turmeric',
                    'Dry brush face gently',
                    'Apply neem and honey mask',
                    'Use light, non-greasy moisturizer'
                ],
                'weekly': [
                    'Exfoliate with turmeric and gram flour - 15 mins',
                    'Ginger and turmeric stimulating massage',
                    'Activated charcoal or clay mask'
                ],
                'monthly': [
                    'Professional deep cleansing facial',
                    'Specialized treatment for oily, congested skin'
                ]
            }
        }
        
        return routines.get(dosha, {'morning': [], 'evening': [], 'weekly': [], 'monthly': []})
    
    def generate_personalized_insights(self, user_name: str, analyses: List[Dict]) -> Dict[str, Any]:
        """Generate complete personalized insights for a user"""
        
        patterns = self.analyze_patterns(analyses)
        questionnaire_insights = self.extract_questionnaire_insights(analyses)
        primary_dosha = patterns.get('primary_dosha')
        season = self.get_current_season()
        
        insights = {
            'user_name': user_name,
            'generated_at': datetime.now().isoformat(),
            'patterns': patterns,
            'questionnaire_insights': questionnaire_insights,
            'current_season': season
        }
        
        if primary_dosha and primary_dosha in self.PRAKRITI_GUIDANCE:
            guidance = self.PRAKRITI_GUIDANCE[primary_dosha]
            seasonal = self.SEASONAL_ADJUSTMENTS.get(season, {})
            
            # FACE ANALYSIS SECTION
            face_analysis = self.analyze_face_concerns(analyses, primary_dosha)
            face_type = self.generate_dosha_face_type(primary_dosha, questionnaire_insights.get('face_shape', ''))
            face_routine = self.generate_face_care_routine(primary_dosha)
            
            insights['primary_dosha'] = primary_dosha
            insights['dosha_element'] = guidance['element']
            insights['characteristics'] = guidance['characteristics']
            insights['imbalance_signs'] = guidance['imbalance_signs']
            
            # Face-specific insights
            insights['face_analysis'] = {
                'face_type': face_type,
                'concerns_analysis': face_analysis,
                'face_care_routine': face_routine
            }
            
            # Generate personalized recommendations
            insights['personalized_recommendations'] = {
                'nutrition': self._personalize_nutrition(guidance, patterns),
                'lifestyle': self._personalize_lifestyle(guidance, patterns),
                'daily_routine': guidance['daily_routine'],
                'seasonal_focus': seasonal.get('focus', 'General wellness'),
                'seasonal_tips': seasonal.get('tips', ''),
                'face_skincare': self._generate_skincare_tips(primary_dosha, face_analysis),
                'priority_actions': self._generate_priority_actions_with_face(primary_dosha, patterns, questionnaire_insights, face_analysis)
            }
        
        return insights
    
    def _generate_skincare_tips(self, dosha: str, face_analysis: Dict) -> List[str]:
        """Generate dosha-specific skincare tips"""
        skincare = []
        
        # Add tips based on recommendations from face analysis
        for recommendation in face_analysis.get('recommendations', []):
            skincare.extend(recommendation.get('tips', [])[:2])  # Top 2 tips per concern
        
        # If no specific concerns, add general tips
        if not skincare:
            if dosha == 'Vata':
                skincare = [
                    'Apply warm sesame oil massage daily for nourishment',
                    'Use hydrating masks with honey and milk weekly',
                    'Avoid harsh chemicals and hot water'
                ]
            elif dosha == 'Pitta':
                skincare = [
                    'Use cooling rose water and sandalwood regularly',
                    'Apply sunscreen daily to protect from sun damage',
                    'Use clay masks to balance excess oil'
                ]
            elif dosha == 'Kapha':
                skincare = [
                    'Use turmeric and gram flour for natural cleansing',
                    'Exfoliate regularly with gentle brushes',
                    'Use lightweight, oil-free moisturizers'
                ]
        
        return skincare
    
    def _generate_priority_actions_with_face(self, dosha: str, patterns: Dict, questionnaire: Dict, face_analysis: Dict) -> List[str]:
        """Generate top 3 priority actions including face health"""
        actions = []
        
        # Add face-specific priority based on concerns
        face_concerns = face_analysis.get('concerns', [])
        if face_concerns:
            primary_concern = face_concerns[0]
            if dosha == 'Vata':
                actions.append(f"Address {primary_concern} by daily oil massage and warm compresses")
            elif dosha == 'Pitta':
                actions.append(f"Reduce {primary_concern} with cooling herbs (neem, turmeric, sandalwood)")
            elif dosha == 'Kapha':
                actions.append(f"Manage {primary_concern} with regular exfoliation and stimulating herbs")
        
        # Add general priority actions
        if dosha == 'Vata':
            actions.extend([
                f"Establish a consistent daily routine - your {questionnaire.get('latest_sleep_pattern', 'variable')} sleep pattern needs stabilization",
                "Practice daily oil massage (abhyanga) in the morning to ground yourself"
            ])
        elif dosha == 'Pitta':
            actions.extend([
                f"Cool down your system - your {questionnaire.get('latest_skin_texture', 'oily')} skin indicates Pitta imbalance",
                "Practice cooling breathing (Sitali pranayama) twice daily"
            ])
        elif dosha == 'Kapha':
            actions.extend([
                f"Increase physical activity - your {questionnaire.get('latest_body_frame', 'solid')} frame needs stimulation",
                "Start with 30-minute cardio exercise 4-5 times per week"
            ])
        
        return actions[:3]
    
    def _personalize_nutrition(self, guidance: Dict, patterns: Dict) -> List[str]:
        """Customize nutrition recommendations based on confidence"""
        recommendations = guidance['nutrition'].copy()
        confidence = patterns.get('average_confidence', 0)
        
        if confidence > 90:
            recommendations.append('Your dosha is very consistent - follow these guidelines strictly')
        elif confidence < 70:
            recommendations.append('Your dosha shows variation - consider consulting an Ayurvedic practitioner')
        
        return recommendations
    
    def _personalize_lifestyle(self, guidance: Dict, patterns: Dict) -> List[str]:
        """Customize lifestyle recommendations"""
        recommendations = guidance['lifestyle'].copy()
        
        if patterns['total_analyses'] < 3:
            recommendations.insert(0, 'Take multiple analyses to better understand your constitution')
        
        return recommendations
    
    def generate_summary_report(self, user_name: str, analyses: List[Dict]) -> str:
        """Generate a formatted text report"""
        insights = self.generate_personalized_insights(user_name, analyses)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PERSONALIZED PRAKRITI INSIGHTS REPORT                     ║
║                          for {user_name.upper()}                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 YOUR CONSTITUTION PROFILE
─────────────────────────────
Primary Dosha: {insights.get('primary_dosha', 'Not determined')}
Element: {insights.get('dosha_element', 'N/A')}
Analysis Consistency: {insights['patterns'].get('consistency', 'N/A')}
Average Confidence: {insights['patterns'].get('average_confidence', 0)}%
Total Analyses: {insights['patterns'].get('total_analyses', 0)}

💫 YOUR CHARACTERISTICS
─────────────────────────────
{insights.get('characteristics', 'Not available')}

⚠️  SIGNS OF IMBALANCE TO WATCH FOR
─────────────────────────────────────
{insights.get('imbalance_signs', 'Not available')}

🍽️  NUTRITION RECOMMENDATIONS
─────────────────────────────────
"""
        for i, rec in enumerate(insights.get('personalized_recommendations', {}).get('nutrition', []), 1):
            report += f"  {i}. {rec}\n"
        
        report += f"""
🏃 LIFESTYLE RECOMMENDATIONS
──────────────────────────────
"""
        for i, rec in enumerate(insights.get('personalized_recommendations', {}).get('lifestyle', []), 1):
            report += f"  {i}. {rec}\n"
        
        report += f"""
⏰ DAILY ROUTINE
─────────────────
{insights.get('personalized_recommendations', {}).get('daily_routine', 'Not available')}

🌍 SEASONAL FOCUS ({insights['current_season'].upper()})
────────────────────
{insights.get('personalized_recommendations', {}).get('seasonal_focus', 'N/A')}
{insights.get('personalized_recommendations', {}).get('seasonal_tips', 'N/A')}

🎯 YOUR PRIORITY ACTIONS
─────────────────────────
"""
        for i, action in enumerate(insights.get('personalized_recommendations', {}).get('priority_actions', []), 1):
            report += f"  {i}. {action}\n"
        
        # Add face analysis section
        face_analysis = insights.get('face_analysis', {})
        if face_analysis:
            face_type = face_analysis.get('face_type', {})
            report += f"""

👤 YOUR FACE TYPE & CHARACTERISTICS
────────────────────────────────────
Face Shape: {face_type.get('face_type', 'Not specified')}
Skin Type: {face_type.get('skin', 'Not specified')}
Features: {face_type.get('features', 'Not specified')}
Typical Issues: {face_type.get('typical_issues', 'Not specified')}
Complexion: {face_type.get('color', 'Not specified')}
"""
            
            # Add face concerns and skincare
            concerns_data = face_analysis.get('concerns_analysis', {})
            if concerns_data.get('recommendations'):
                report += f"""
💆 YOUR FACE CARE RECOMMENDATIONS
──────────────────────────────────
"""
                for rec in concerns_data.get('recommendations', []):
                    report += f"\n{rec.get('concern', 'Face Care').upper()}\n"
                    report += f"└─ Why: {rec.get('cause', 'Natural skin condition')}\n"
                    report += "└─ Quick Tips:\n"
                    for tip in rec.get('tips', [])[:3]:  # Top 3 tips per concern
                        report += f"   • {tip}\n"
            
            # Add face care routine
            routine = face_analysis.get('face_care_routine', {})
            if routine:
                report += f"""

📅 YOUR PERSONALIZED FACE CARE ROUTINE
───────────────────────────────────────
MORNING:
"""
                for item in routine.get('morning', []):
                    report += f"  • {item}\n"
                
                report += f"""
EVENING:
"""
                for item in routine.get('evening', []):
                    report += f"  • {item}\n"
                
                report += f"""
WEEKLY TREATMENT:
"""
                for item in routine.get('weekly', []):
                    report += f"  • {item}\n"
                
                report += f"""
MONTHLY TREATMENT:
"""
                for item in routine.get('monthly', []):
                    report += f"  • {item}\n"
        
        # Add skincare tips
        skincare_tips = insights.get('personalized_recommendations', {}).get('face_skincare', [])
        if skincare_tips:
            report += f"""

🧴 SKINCARE ESSENTIALS FOR YOUR SKIN
─────────────────────────────────────
"""
            for i, tip in enumerate(skincare_tips, 1):
                report += f"  {i}. {tip}\n"
        
        report += f"""

╚══════════════════════════════════════════════════════════════════════════════╝
Generated: {insights['generated_at']}
"""
        
        return report


def generate_insights_for_user(user_name: str, user_id: str, app_data_path: str = None) -> Dict[str, Any]:
    """Main function to generate insights for a user"""
    
    if app_data_path is None:
        app_data_path = r'c:\Users\dhira\Downloads\prakriti-ai-ready-deploy\data\app-data.json'
    
    try:
        with open(app_data_path, 'r') as f:
            data = json.load(f)
        
        # Get all analyses for this user
        user_analyses = [a for a in data.get('analyses', []) if a.get('userId') == user_id]
        
        insights_gen = PrakritiInsights()
        insights = insights_gen.generate_personalized_insights(user_name, user_analyses)
        
        return {
            'success': True,
            'data': insights
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
