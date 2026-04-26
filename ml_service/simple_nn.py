import random
import math


def _softmax(logits):
    max_logit = max(logits)
    exp_vals = [math.exp(x - max_logit) for x in logits]
    total = sum(exp_vals)
    return [x / total for x in exp_vals]


def _tanh(x):
    return math.tanh(x)


def _tanh_derivative(x):
    return 1.0 - x * x


def _dot(vec_a, vec_b):
    return sum(a * b for a, b in zip(vec_a, vec_b))


def _matrix_vector_mul(matrix, vector):
    return [_dot(row, vector) for row in matrix]


def _vector_add(a, b):
    return [x + y for x, y in zip(a, b)]


def _vector_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def _scalar_mul(vector, scalar):
    return [x * scalar for x in vector]


def _outer_product(vec_a, vec_b):
    return [[a * b for b in vec_b] for a in vec_a]


class SimpleNN:
    def __init__(self, input_size=12, hidden_size=16, output_size=3, seed=42, dropout_rate=0.2):
        random.seed(seed)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dropout_rate = dropout_rate
        self.classes = ['Vata', 'Pitta', 'Kapha']

        self.W1 = [[random.uniform(-0.3, 0.3) for _ in range(input_size)] for _ in range(hidden_size)]
        self.b1 = [0.0] * hidden_size
        self.W2 = [[random.uniform(-0.3, 0.3) for _ in range(hidden_size)] for _ in range(output_size)]
        self.b2 = [0.0] * output_size

    def _apply_dropout(self, activations):
        return [a * (random.random() > self.dropout_rate) for a in activations]

    def _batch_normalize(self, activations):
        mean = sum(activations) / len(activations)
        variance = sum((a - mean) ** 2 for a in activations) / len(activations)
        return [(a - mean) / (variance ** 0.5 + 1e-8) for a in activations]

    def _forward_one(self, x, training=False):
        z1 = _vector_add(_matrix_vector_mul(self.W1, x), self.b1)
        a1 = [_tanh(v) for v in z1]
        a1 = self._batch_normalize(a1)
        if training:
            a1 = self._apply_dropout(a1)
        else:
            a1 = [a * (1.0 - self.dropout_rate) for a in a1]
        z2 = _vector_add(_matrix_vector_mul(self.W2, a1), self.b2)
        yhat = _softmax(z2)
        return a1, yhat

    def predict_proba(self, X):
        return [self._forward_one(x, training=False)[1] for x in X]

    def predict(self, X):
        return [self.classes[probs.index(max(probs))] for probs in self.predict_proba(X)]

    def _one_hot(self, label):
        vector = [0.0] * self.output_size
        index = self.classes.index(label)
        vector[index] = 1.0
        return vector

    def train(self, X, y, epochs=100, learning_rate=0.05, verbose=True):
        data = list(zip(X, y))
        for epoch in range(epochs):
            random.shuffle(data)
            total_loss = 0.0
            for x, label in data:
                a1, yhat = self._forward_one(x, training=True)
                y_true = self._one_hot(label)
                loss = -sum(t * math.log(max(p, 1e-15)) for t, p in zip(y_true, yhat))
                total_loss += loss

                output_error = [p - t for p, t in zip(yhat, y_true)]
                grad_W2 = _outer_product(output_error, a1)
                grad_b2 = output_error

                hidden_errors = [0.0] * self.hidden_size
                for j in range(self.hidden_size):
                    hidden_errors[j] = sum(self.W2[k][j] * output_error[k] for k in range(self.output_size)) * _tanh_derivative(a1[j])

                grad_W1 = _outer_product(hidden_errors, x)
                grad_b1 = hidden_errors

                for i in range(self.output_size):
                    for j in range(self.hidden_size):
                        self.W2[i][j] -= learning_rate * grad_W2[i][j]
                    self.b2[i] -= learning_rate * grad_b2[i]

                for i in range(self.hidden_size):
                    for j in range(self.input_size):
                        self.W1[i][j] -= learning_rate * grad_W1[i][j]
                    self.b1[i] -= learning_rate * grad_b1[i]

            if verbose and (epoch + 1) % 20 == 0:
                accuracy = self.evaluate(X, y)
                print(f'Epoch {epoch + 1}/{epochs} - loss={total_loss:.4f} - accuracy={accuracy:.3f}')

        return self.evaluate(X, y)

    def evaluate(self, X, y):
        predictions = self.predict(X)
        correct = sum(1 for pred, truth in zip(predictions, y) if pred == truth)
        return correct / len(X) if X else 0.0
