import numpy as np


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
        self.value = np.mean(y)
        if self.max_depth is not None and depth >= self.max_depth:
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
        if self.left is None and self.right is None:
            return self.value

        if x[self.feature_index] is None:
            return self.value

        if x[self.feature_index] <= self.threshold:
            return self.left.predict_instance(x)
        else:
            return self.right.predict_instance(x)

    def predict(self, X):
        return np.array([self.predict_instance(x) for x in X])

    def get_weights(self):
        weights = []
        nodes = [self]

        while len(nodes) > 0:
            node = nodes.pop()
            if node is None:
                continue
            if node.left is None and node.right is None:
                weights.append((0, node.max_depth, node.value))
            else:
                weights.append((1, node.max_depth, node.value, node.feature_index, node.threshold))
            nodes.append(node.right)
            nodes.append(node.left)

        return weights

    def _assign_weight(self, weight):
        self.feature_index = None
        self.threshold = None
        self.left = None
        self.right = None
        self.value = weight[2]
        self.max_depth = weight[1]
        if weight[0] == 1:
            self.feature_index = weight[3]
            self.threshold = weight[4]

    def set_weights(self, weights):
        parents = [self]

        for w in weights:
            parents[-1]._assign_weight(w)
            if w[0] == 0:
                parents.pop()
                if len(parents) == 0:
                    return
                while parents[-1].right is not None:
                    parents.pop()
                    if len(parents) == 0:
                        return
                new = DecisionTreeClassifier()
                parents[-1].right = new
                parents.append(new)
            else:
                new = DecisionTreeClassifier()
                parents[-1].left = new
                parents.append(new)
