import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Configuration ---
DATA_PATH = "data/synthetic_admissions_data.csv"
MODEL_DIR = "src/core/ml_models/"
MODEL_PATH = os.path.join(MODEL_DIR, "admission_model.pkl")

def train_model():
    """
    Loads data, trains, evaluates, and saves the model artifact (model + columns).
    """
    print("--- Starting Model Training ---")

    # 1. Load Data
    try:
        df = pd.read_csv(DATA_PATH)
        logging.info(f"Successfully loaded dataset with {len(df)} records from {DATA_PATH}.")
    except FileNotFoundError:
        logging.error(
            f"FATAL ERROR: Data file not found at \"{DATA_PATH}\". Please run generate_synthetic_data.py first."
        )
        return

    # 2. Feature Engineering
    logging.info("Performing one-hot encoding on 'applied_major_category'...")
    try:
        df_encoded = pd.get_dummies(df, columns=["applied_major_category"], prefix="major")
    except Exception as e:
        logging.error(f"FATAL ERROR: Failed during one-hot encoding. Error: {e}")
        return

    # Define features (X) and target (y)
    X = df_encoded.drop("admission_decision", axis=1)
    y = df_encoded["admission_decision"]

    # 3. Split Data for Training and Testing
    logging.info("Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Train the Machine Learning Model
    logging.info("Training the Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)
    logging.info("Model training complete.")

    # 5. Evaluate the Model
    logging.info("--- Evaluating Model Performance on Test Data ---")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Rejected (0)", "Admitted (1)"]))

    # 6. Save the Model and its Columns Together (The Artifact)
    logging.info("--- Saving Trained Model and Column Blueprint ---")
    model_artifact = {
        "model": model,
        "columns": list(X.columns),  # Save the exact column names and order
    }
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model_artifact, MODEL_PATH)
    logging.info(f"✅ Model artifact successfully saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model() 