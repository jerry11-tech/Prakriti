import os
import pickle
import json
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
LATEST_MODEL_FILENAME = os.path.join(MODEL_DIR, 'prakriti_model_latest.pkl')
META_FILENAME = os.path.join(MODEL_DIR, 'prakriti_model_latest.meta.json')

os.makedirs(MODEL_DIR, exist_ok=True)


def _version_stamp():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def save_model(model, metadata=None):
    version = metadata.get('version') if metadata else None
    version = version or _version_stamp()
    filename = os.path.join(MODEL_DIR, f'prakriti_model_{version}.pkl')
    meta_filename = os.path.join(MODEL_DIR, f'prakriti_model_{version}.meta.json')

    with open(filename, 'wb') as f:
        pickle.dump(model, f)

    meta = {
        'version': version,
        'saved_at': datetime.utcnow().isoformat() + 'Z',
        'filename': os.path.abspath(filename),
        'metadata': metadata or {}
    }
    with open(meta_filename, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    with open(LATEST_MODEL_FILENAME, 'wb') as f:
        pickle.dump(model, f)
    with open(META_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    return filename


def load_model(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_latest_model():
    return load_model(LATEST_MODEL_FILENAME)


def list_models():
    if not os.path.isdir(MODEL_DIR):
        return []
    models = []
    for name in os.listdir(MODEL_DIR):
        if name.endswith('.meta.json') and 'latest' not in name:
            models.append(name)
    return sorted(models)
