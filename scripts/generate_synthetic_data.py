import csv
import json
import random
import pandas as pd

# Configuration
NUM_PROFILES = 5000
OUTPUT_FILE = 'data/synthetic_quiz_profiles.jsonl'

# Get the quiz questions to define the universe of possible answers
# This is a simplified version of the quiz questions from web_templates/quiz/script.js
# to ensure we generate valid answers.
QUIZ_STRUCTURE = {
    "study_format": ["ការបង្រៀន", "ការអនុវត្ត", "ការងារជាក្រុម"],
    "study_hours": ["តិចជាង ១០", "១០-២០", "២០-៣០", "ច្រើនជាង ៣០"],
    "fav_subjects": ["គណិតវិទ្យា", "វិទ្យាសាស្ត្រ", "ភាសា", "សិល្បៈ", "សង្គម"],
    "job_interest": ["វិស្វករ", "គ្រូពេទ្យ", "គ្រូបង្រៀន", "អ្នកជំនួញ", "សិល្បករ", "អ្នកបង្កើតកម្មវិធី", "អ្នកទីផ្សារ"],
    "work_style": ["ម្នាក់ឯង", "ជាក្រុម", "ជាអ្នកដឹកនាំ", "ជាអ្នកតាម"],
    "company_type": ["រដ្ឋាភិបាល", "ឯកជន", "ក្រុមហ៊ុនបច្ចេកវិទ្យាថ្មី (Startup)", "អង្គការមិនស្វែងរកប្រាក់ចំណេញ"],
    "value_priority": ["ប្រាក់ខែ", "ស្ថិរភាព", "តុល្យភាពការងារនិងជីវិត", "ការរីកចម្រើន"],
    "social_preference": ["ចូលចិត្តខ្លាំង", "មធ្យម", "មិនចូលចិត្ត"],
    "future_aspiration": ["អ្នកជំនាញ", "អ្នកគ្រប់គ្រង", "ម្ចាស់អាជីវកម្ម", "អ្នកធ្វើការឯករាជ្យ"],
    "stress_tolerance": ["ល្អណាស់", "មធ្យម", "មិនល្អ"],
    "location": ["ភ្នំពេញ", "សៀមរាប", "បាត់ដំបង", "គ្រប់ទីកន្លែង"],
    "gpa": ["A", "B", "C", "D", "E"],
    "budget": ["<$500", "$500-$1000", "$1000-$2000", ">$2000"],
    "english_proficiency": ["ល្អណាស់", "មធ្យម", "តិចតួច"]
}

# Define Personas
# Each persona has preferred answers and weights for each question.
# The weights determine the probability of picking an answer.
PERSONAS = {
    "tech_enthusiast": {
        "fav_subjects": {"គណិតវិទ្យា": 5, "វិទ្យាសាស្ត្រ": 3},
        "job_interest": {"អ្នកបង្កើតកម្មវិធី": 5, "វិស្វករ": 3},
        "work_style": {"ម្នាក់ឯង": 4, "ជាក្រុម": 2},
        "company_type": {"ក្រុមហ៊ុនបច្ចេកវិទ្យាថ្មី (Startup)": 5, "ឯកជន": 3},
        "value_priority": {"ការរីកចម្រើន": 5, "ប្រាក់ខែ": 3},
        "study_hours": {"ច្រើនជាង ៣០": 4, "២០-៣០": 3},
        "gpa": {"A": 4, "B": 3},
        "english_proficiency": {"ល្អណាស់": 5},
    },
    "humanities_scholar": {
        "fav_subjects": {"ភាសា": 5, "សិល្បៈ": 4, "សង្គម": 3},
        "job_interest": {"គ្រូបង្រៀន": 4, "សិល្បករ": 4},
        "work_style": {"ម្នាក់ឯង": 5, "ជាអ្នកតាម": 2},
        "company_type": {"អង្គការមិនស្វែងរកប្រាក់ចំណេញ": 4, "រដ្ឋាភិបាល": 2},
        "value_priority": {"តុល្យភាពការងារនិងជីវិត": 5},
        "social_preference": {"មិនចូលចិត្ត": 3, "មធ្យម": 2},
        "future_aspiration": {"អ្នកជំនាញ": 4, "អ្នកធ្វើការឯករាជ្យ": 3},
        "study_format": {"ការបង្រៀន": 5},
    },
    "business_leader": {
        "fav_subjects": {"សង្គម": 4, "ភាសា": 2},
        "job_interest": {"អ្នកជំនួញ": 5, "អ្នកទីផ្សារ": 4, "អ្នកគ្រប់គ្រង": 3},
        "work_style": {"ជាអ្នកដឹកនាំ": 5, "ជាក្រុម": 4},
        "company_type": {"ឯកជន": 5, "ក្រុមហ៊ុនបច្ចេកវិទ្យាថ្មី (Startup)": 2},
        "value_priority": {"ប្រាក់ខែ": 5, "ការរីកចម្រើន": 4},
        "social_preference": {"ចូលចិត្តខ្លាំង": 5},
        "future_aspiration": {"ម្ចាស់អាជីវកម្ម": 5, "អ្នកគ្រប់គ្រង": 4},
        "stress_tolerance": {"ល្អណាស់": 4, "មធ្យម": 2},
    },
    "health_medic": {
        "fav_subjects": {"វិទ្យាសាស្ត្រ": 5},
        "job_interest": {"គ្រូពេទ្យ": 5},
        "work_style": {"ជាក្រុម": 4},
        "company_type": {"រដ្ឋាភិបាល": 4, "ឯកជន": 2},
        "value_priority": {"ស្ថិរភាព": 5},
        "social_preference": {"ចូលចិត្តខ្លាំង": 4},
        "future_aspiration": {"អ្នកជំនាញ": 5},
        "stress_tolerance": {"ល្អណាស់": 5},
        "study_hours": {"ច្រើនជាង ៣០": 5},
        "gpa": {"A": 5, "B": 2},
    }
}

def choose_weighted(choices, weights):
    """Helper to make a weighted random choice."""
    return random.choices(choices, weights=weights, k=1)[0]

def generate_profile():
    """Generates a single synthetic user profile."""
    # 1. Pick a base persona
    persona_name = random.choice(list(PERSONAS.keys()))
    persona = PERSONAS[persona_name]
    
    profile = {"persona": persona_name, "answers": {}}

    # 2. Generate answers for each question
    for key, options in QUIZ_STRUCTURE.items():
        # Check if the persona has a preference for this question
        if key in persona:
            # Create weights for each option, defaulting to 1 if not specified
            weights = [persona[key].get(opt, 1) for opt in options]
            
            # For multiple choice questions, we can select more than one
            if key in ["fav_subjects", "job_interest"]:
                num_choices = random.randint(1, 2) # Select 1 or 2 options
                # Use weighted choice to pick multiple items
                # This is a bit tricky, we'll simplify by just picking the top N weighted choices
                # A more robust way would be to sample multiple times.
                sorted_options = sorted(zip(options, weights), key=lambda x: x[1], reverse=True)
                profile["answers"][key] = [opt for opt, w in sorted_options[:num_choices]]
            else: # Single choice
                profile["answers"][key] = choose_weighted(options, weights)
        else:
            # If no preference, choose randomly
            if key in ["fav_subjects", "job_interest"]:
                 profile["answers"][key] = random.sample(options, k=random.randint(1, 2))
            else:
                 profile["answers"][key] = random.choice(options)
                
    return profile


def main(num_records: int = 5000, output_file: str = None) -> pd.DataFrame:
    """
    Main function to generate profiles.

    Args:
        num_records: The number of synthetic profiles to generate.
        output_file: (Optional) Path to save the generated data as a JSONL file.

    Returns:
        A pandas DataFrame containing the generated data.
    """
    print(f"Generating {num_records} synthetic user profiles...")
    
    profiles_list = [generate_profile() for _ in range(num_records)]

    if output_file:
        print(f"Saving generated data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for profile in profiles_list:
                f.write(json.dumps(profile, ensure_ascii=False) + '\n')
        print("Save complete.")

    # Convert to DataFrame for use in other scripts
    # We need to flatten the nested dictionary
    records = []
    for p in profiles_list:
        flat_record = p['answers'].copy()
        # For ML, we need a single target variable. We'll use the top job interest.
        # This is a simplification; a real model might predict probabilities for all majors.
        top_job = flat_record.get("job_interest", [])[0] if flat_record.get("job_interest") else "Unknown"

        # A simple mapping from job interest to major category
        # This should align with major_profiles.py for consistency
        job_to_major_map = {
            "អ្នកបង្កើតកម្មវិធី": "Technology", "វិស្វករ": "Engineering",
            "គ្រូពេទ្យ": "Health Sciences", "អ្នកជំនួញ": "Business & Management",
            "អ្នកទីផ្សារ": "Marketing", "គ្រូបង្រៀន": "Education",
            "សិល្បករ": "Arts & Humanities"
        }
        recommended_major = job_to_major_map.get(top_job, "Social Sciences") # Default

        records.append({
            "user_profile": flat_record,
            "recommended_major": recommended_major
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    main(num_records=NUM_PROFILES, output_file=OUTPUT_FILE)
