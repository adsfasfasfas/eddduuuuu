import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import json

print("--- Starting Recommendation Model Training ---")

# Load the synthetic data
file_path = 'data/synthetic_quiz_profiles.jsonl'
print(f"Loading data from {file_path}...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]
print(f"Loaded {len(data)} records.")

# Extract features and create a DataFrame
features = [item['answers'] for item in data]
df = pd.DataFrame(features)

# --- 1. Label Engineering ---
# A mapping from the primary job interest to a major category.
# This defines the prediction target for the model.
job_to_major_map = {
    "អ្នកបង្កើតកម្មវិធី": "Technology", "វិស្វករ": "Engineering",
    "គ្រូពេទ្យ": "Health Sciences", "អ្នកជំនួញ": "Business & Management",
    "អ្នកទីផ្សារ": "Marketing", "គ្រូបង្រៀន": "Education",
    "សិល្បករ": "Arts & Humanities"
}

def get_major_from_interest(job_interest_list):
    """Safely extracts the first job interest and maps it to a major."""
    if isinstance(job_interest_list, list) and job_interest_list:
        # Use the first interest as the primary one for the label
        return job_to_major_map.get(job_interest_list[0], "Social Sciences")
    return "Social Sciences" # Default category

df['major'] = df['job_interest'].apply(get_major_from_interest)
print("Created 'major' target labels.")

# --- 2. Feature Engineering ---
# The model cannot handle lists directly. We will convert list-based features
# into a single string so the OneHotEncoder can process them.
multi_value_features = ['fav_subjects', 'job_interest']
for col in multi_value_features:
    # Sort items to ensure consistency (e.g., "Art, Math" is same as "Math, Art")
    # and join them into a single string.
    df[col] = df[col].apply(lambda x: ', '.join(sorted(x)) if isinstance(x, list) else "")
print("Processed multi-value features into strings.")

# Define all features to be used for training.
categorical_features = [
    'study_format', 'study_hours', 'fav_subjects', 'job_interest', 'work_style',
    'company_type', 'value_priority', 'social_preference', 'future_aspiration',
    'stress_tolerance', 'location', 'gpa', 'budget', 'english_proficiency'
]

# --- 3. Model Pipeline Setup ---
# We use a ColumnTransformer to apply OneHotEncoding to all our categorical features.
# This converts text categories into a numerical format for the model.
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

# The final pipeline includes preprocessing and the classifier.
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])
print("Model pipeline created.")

# --- 4. Training and Evaluation ---
# Split data into training and testing sets.
# Using 'stratify' ensures the distribution of majors is the same in both sets,
# which is crucial for training a reliable model.
X = df[categorical_features]
y = df['major']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Data split into {len(X_train)} training and {len(X_test)} testing samples.")

# Train the model
print("Training the RandomForestClassifier...")
model.fit(X_train, y_train)
print("Training complete.")

# Evaluate the model's performance on the test set
print("--- Model Evaluation Report ---")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# --- 5. Save the Model ---
model_path = 'src/core/ml_models/recommendation_model.pkl'
print(f"Saving the trained model to {model_path}...")
joblib.dump(model, model_path)
print(f"✅ Model successfully saved!")
print("--- End of Training Script ---")
