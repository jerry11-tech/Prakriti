import os
from data_utils import load_training_dataset
from simple_nn import SimpleNN
from model_store import save_model, load_latest_model
from sklearn.metrics import precision_score, recall_score, f1_score


def run_training(epochs=100, learning_rate=0.08):
    X, y = load_training_dataset()
    print(f'Loaded {len(X)} records for training.')

    if len(X) < 50:
        print('Not enough historical data found; generating synthetic dataset for model warm-up.')
        X, y = load_training_dataset(augment=True)
        print(f'Backfilled dataset to {len(X)} records.')

    existing_model = load_latest_model()
    if existing_model:
        print('Existing model found. Continuing incremental training from latest model weights.')
        model = existing_model
    else:
        print('No existing model found. Starting training from scratch.')
        model = SimpleNN()

    accuracy = model.train(X, y, epochs=epochs, learning_rate=learning_rate)
    print(f'Model training complete. Validation accuracy: {accuracy * 100:.2f}%')

    # Evaluate on the training set
    predictions = model.predict(X)
    precision = precision_score(y, predictions, average='weighted')
    recall = recall_score(y, predictions, average='weighted')
    f1 = f1_score(y, predictions, average='weighted')

    print(f'Precision: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1:.2f}')

    saved_path = save_model(model, metadata={
        'training_samples': len(X),
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'model_type': 'SimpleNN'
    })
    print(f'Model saved to: {saved_path}')


if __name__ == '__main__':
    run_training()
