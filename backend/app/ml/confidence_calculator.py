"""Confidence calculator for anomaly detection predictions.

Isolates and documents the boundary distance calculations used to resolve 
model inference confidences.
"""

import numpy as np

class ConfidenceCalculator:
    """Computes confidence scores based on Isolation Forest boundary distances.

    Distance Explanation:
        The Isolation Forest decision function returns raw anomaly scores, where:
          - Values close to 0.0 indicate the sample is situated directly near the
            decision boundary (high uncertainty, low confidence).
          - Values far from 0.0 (approaching -0.5 for outliers and +0.5 for inliers)
            indicate the sample is far from the boundary (high certainty, high confidence).

        Mathematical Formula:
          Confidence = Clip(2.0 * |Decision Score|, 0.0, 1.0)
    """

    def calculate(self, decision_scores: np.ndarray) -> np.ndarray:
        """Calculates normalized confidence values [0.0, 1.0] from decision scores.

        Args:
            decision_scores: Numpy array containing Isolation Forest decision function values.

        Returns:
            np.ndarray: Normalized confidence values.
        """
        return np.clip(2.0 * np.abs(decision_scores), 0.0, 1.0)
