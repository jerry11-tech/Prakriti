import os
import json
import csv
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'app-data.json')


CLASS_LABELS = ['Vata', 'Pitta', 'Kapha']


def _normalize_body(value):
    value = str(value or '').lower()
    if 'slim' in value or 'thin' in value or 'light' in value:
        return 0
    if 'medium' in value or 'average' in value:
        return 1
    return 2


def _normalize_skin(value):
    value = str(value or '').lower()
    if 'dry' in value or 'sensitive' in value:
        return 0
    if 'oily' in value or 'smooth' in value:
        return 1
    return 2


def _normalize_sleep(value):
    value = str(value or '').lower()
    if 'light' in value or 'short' in value:
        return 0
    if 'moderate' in value or 'regular' in value:
        return 1
    return 2


def _parse_record(record):
    answers = record.get('questionnaireData', {})
    target = record.get('prakritiResult')
    if not target or target not in CLASS_LABELS:
        return None
        
    # We identify 12 specific keys that must exist or be mapped
    keys = [
        'bodyFrame', 'skinTexture', 'sleepPattern', 'digestion', 
        'appetite', 'temperament', 'energy', 'memory', 
        'speech', 'bowels', 'weather', 'activity'
    ]
    
    features = []
    # Simplified mapping for all 12
    for k in keys:
        val = str(answers.get(k, '')).lower()
        if any(w in val for w in ['slim', 'dry', 'light', 'irregular', 'variable', 'anxious', 'fluctuating', 'quick', 'fast', 'humid']):
            features.append(0)
        elif any(w in val for w in ['medium', 'oily', 'sound', 'strong', 'intense', 'focused', 'high', 'sharp', 'clear', 'cool']):
            features.append(1)
        else:
            features.append(2)
            
    if len(features) < 12:
        return None

    return {
        'features': features,
        'target': target
    }


def load_app_records():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            payload = json.load(f)
        except:
            return []

    records = []
    for analysis in payload.get('analyses', []):
        parsed = _parse_record(analysis)
        if parsed:
            records.append(parsed)
    return records


def _scan_external_datasets(root=None):
    return [] # Skipping CSV for now to avoid dimension mismatch unless they are updated


def generate_synthetic_records(samples=1000):
    random.seed(42)
    records = []
    for _ in range(samples):
        # Generate 12 features
        f = [random.choice([0, 1, 2]) for _ in range(12)]
        score = sum(f) / 12.0 # Normalized score
        
        if score < 0.8:
            target = 'Vata'
        elif score < 1.4:
            target = 'Pitta'
        else:
            target = 'Kapha'
        records.append({'features': f, 'target': target})
    return records


def load_training_dataset(augment=False):
    records = load_app_records()
    external = _scan_external_datasets()
    records.extend(external)

    if augment or len(records) < 50:
        synthetic = generate_synthetic_records(samples=500)
        records.extend(synthetic)

    features = [record['features'] for record in records]
    labels = [record['target'] for record in records]
    return features, labels
