"""Model definition for event risk or severity prediction."""


class RiskModel:
    """Container for the trained classifier or regressor."""

    def __init__(self, model=None):
        self.model = model

    def predict(self, features):
        """Predict event risk or severity from engineered features."""
        if self.model is None:
            raise NotImplementedError("Attach a trained model before inference.")
        return self.model.predict(features)