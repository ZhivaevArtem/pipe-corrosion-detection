import os

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score


class DecisionTreeClassifier:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.feature_index = None
        self.threshold = None
        self.left = None
        self.right = None
        self.value = None

    def mse(self, y):
        mean = np.mean(y)
        return np.mean((y - mean) ** 2)

    def split(self, X, y, feature_index, threshold):
        left_indices = X[:, feature_index] <= threshold
        right_indices = ~left_indices
        return X[left_indices], y[left_indices], X[right_indices], y[right_indices]

    def find_best_split(self, X, y):
        best_mse = np.inf
        best_feature_index = None
        best_threshold = None

        for feature_index in range(X.shape[1]):
            unique_values = np.unique(X[:, feature_index])
            thresholds = (unique_values[:-1] + unique_values[1:]) / 2

            for threshold in thresholds:
                X_left, y_left, X_right, y_right = self.split(X, y, feature_index, threshold)

                mse_left = self.mse(y_left)
                mse_right = self.mse(y_right)

                total_mse = (mse_left * len(y_left) + mse_right * len(y_right)) / len(y)

                if total_mse < best_mse:
                    best_mse = total_mse
                    best_feature_index = feature_index
                    best_threshold = threshold

        return best_feature_index, best_threshold

    def build_tree(self, X, y, depth):
        if self.max_depth is not None and depth >= self.max_depth:
            self.value = np.mean(y)
            return

        feature_index, threshold = self.find_best_split(X, y)

        if feature_index is None or threshold is None:
            self.value = np.mean(y)
            return

        self.feature_index = feature_index
        self.threshold = threshold

        X_left, y_left, X_right, y_right = self.split(X, y, feature_index, threshold)

        self.left = DecisionTreeClassifier(max_depth=self.max_depth)
        self.left.build_tree(X_left, y_left, depth + 1)

        self.right = DecisionTreeClassifier(max_depth=self.max_depth)
        self.right.build_tree(X_right, y_right, depth + 1)

    def fit(self, X, y):
        self.build_tree(X, y, depth=0)

    def predict_instance(self, x):
        if self.value is not None:
            return self.value

        if x[self.feature_index] <= self.threshold:
            return self.left.predict_instance(x)
        else:
            return self.right.predict_instance(x)

    def predict(self, X):
        return np.array([self.predict_instance(x) for x in X])
