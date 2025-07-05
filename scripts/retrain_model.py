import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import json

print("--- Starting Recommendation Model Retraining ---")

# Load the feedback data
file_path = 'data/feedback.jsonl'
print(f"Loading data from {file_path}...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]
print(f"Loaded {len(data)} feedback records.")

# Extract features and labels
features = [item['user_profile'] for item in data]
labels = [item['major_name'] for item in data]

df = pd.DataFrame(features)
df['major'] = labels

# Feature Engineering
multi_value_features = ['fav_subjects', 'job_interest']
for col in multi_value_features:
    df[col] = df[col].apply(lambda x: ', '.join(sorted(x)) if isinstance(x, list) else "")
print("Processed multi-value features into strings.")

categorical_features = [
    'study_format', 'study_hours', 'fav_subjects', 'job_interest', 'work_style',
    'company_type', 'value_priority', 'social_preference', 'future_aspiration',
    'stress_tolerance', 'location', 'gpa', 'budget', 'english_proficiency'
]

# Model Pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])
print("Model pipeline created.")

# Train the model
print("Retraining the RandomForestClassifier on all available feedback data...")
model.fit(df[categorical_features], df['major'])
print("Retraining complete.")

# Save the model
model_path = 'src/core/ml_models/recommendation_model.pkl'
print(f"Saving the retrained model to {model_path}...")
joblib.dump(model, model_path)
print(f"✅ Model successfully saved!")
print("--- End of Retraining Script ---")
