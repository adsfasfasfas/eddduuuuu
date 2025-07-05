import joblib

def load_model():
    """Loads the trained recommendation model."""
    return joblib.load("src/core/ml_models/recommendation_model.pkl")
