import numpy as np

from Decision_Tree import DecisionTreeClassifier


class GradientBoostingClassifier:
    def __init__(self, n_estimators=10, learning_rate=0.1, max_depth=None):
        self.ensemble_size = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.ensemble = []
        self.initial_prediction = None

    def fit(self, X, y):
        self.initial_prediction = np.mean(y)

        for _ in range(self.ensemble_size):
            residuals = y - self.predict(X)

            tree = DecisionTreeClassifier(max_depth=self.max_depth)
            tree.fit(X, residuals)

            self.ensemble.append(tree)

    def predict(self, X):
        pred = self.initial_prediction
        for e in self.ensemble:
            pred += self.learning_rate * e.predict(X)
        return pred

    def predictb(self, X):
        return np.array([0 if p < .5 else 1 for p in self.predict(X)])

    def get_weights(self):
        weights = (
            self.ensemble_size,
            self.learning_rate,
            self.max_depth,
            self.initial_prediction,
            [e.get_weights() for e in self.ensemble],
        )
        return weights

    def set_weights(self, weights):
        self.ensemble_size = weights[0]
        self.learning_rate = weights[1]
        self.max_depth = weights[2]
        self.initial_prediction = weights[3]
        self.ensemble = []
        for w in weights[4]:
            tree = DecisionTreeClassifier()
            tree.set_weights(w)
            self.ensemble.append(tree)
