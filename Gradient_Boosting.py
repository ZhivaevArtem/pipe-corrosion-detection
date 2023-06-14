import numpy as np
import pandas as pd
import os

from sklearn.metrics import accuracy_score

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
