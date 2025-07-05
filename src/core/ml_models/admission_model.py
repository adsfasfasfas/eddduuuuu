import joblib
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = "src/core/ml_models/admission_model.pkl"

def load_model():
    """
    Loads the trained admission prediction model from the file.
    Returns the model artifact or None if it fails.
    """
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Admission model file not found at {MODEL_PATH}. Prediction features will be disabled.")
        return None
    try:
        model_artifact = joblib.load(MODEL_PATH)
        return model_artifact
    except Exception as e:
        logger.error(f"Error loading admission model: {e}", exc_info=True)
        return None 