import json
import datetime
import joblib
import logging
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class Recommender:
    """
    The intelligent recommendation engine for EduGuideBot.
    Provides personalized recommendations for majors and universities.
    """
    def __init__(self, universities: List[Dict[str, Any]], major_profiles: List[Dict[str, Any]], admission_model: Any):
        self.universities = pd.DataFrame(universities)
        self.major_profiles = pd.DataFrame(major_profiles)
        self.admission_model = admission_model
        self.recommendation_model = self._load_recommendation_model()

    def _load_recommendation_model(self):
        model_path = "src/core/ml_models/recommendation_model.pkl"
        try:
            model = joblib.load(model_path)
            logger.info(f"Successfully loaded recommendation model from {model_path}")
            return model
        except FileNotFoundError:
            logger.warning(f"Recommendation model not found at {model_path}. Using rule-based fallback.")
            return None
        except Exception as e:
            logger.error(f"Error loading recommendation model: {e}")
            return None

    def get_major_recommendations(self, user_profile: Dict[str, Any], top_n: int = 3) -> Tuple[List[Dict[str, Any]], int]:
        """
        Recommends majors based on a compatibility score, using the ML model if available.
        """
        scores = []

        if self.recommendation_model:
            logger.info("Using ML model for major recommendations.")
            for index, major in self.major_profiles.iterrows():
                features = self._prepare_features_for_major_recommendation(major, user_profile)
                logger.info(f"Features for {major['major_name_en']}: {features}")
                try:
                    # Assuming the model predicts a single score
                    score = self.recommendation_model.predict([features])[0]
                    reasons = ["ML Model Prediction"]
                    logger.info(f"ML model predicted score for {major['major_name_en']}: {score}")
                except Exception as e:
                    logger.warning(f"ML model prediction failed for major {major['major_name_en']}: {e}. Falling back to rule-based.")
                    score, reasons = self._calculate_major_compatibility(major, user_profile)
                    logger.info(f"Rule-based score for {major['major_name_en']}: {score}, Reasons: {reasons}")
                
                scores.append({
                    "major_name": major['major_name'],
                    "major_name_en": major['major_name_en'],
                    "score": score,
                    "description": major['description'],
                    "reason": ", ".join(reasons)
                })
        else:
            logger.info("Using rule-based system for major recommendations (ML model not loaded).")
            for index, major in self.major_profiles.iterrows():
                score, reasons = self._calculate_major_compatibility(major, user_profile)
                logger.info(f"Rule-based score for {major['major_name_en']}: {score}, Reasons: {reasons}")
                scores.append({
                    "major_name": major['major_name'],
                    "major_name_en": major['major_name_en'],
                    "score": score,
                    "description": major['description'],
                    "reason": ", ".join(reasons)
                })

        logger.info(f"All major scores: {scores}")
        sorted_majors = sorted(scores, key=lambda x: x["score"], reverse=True)
        logger.info(f"Sorted majors: {sorted_majors}")
        max_score = sorted_majors[0]['score'] if sorted_majors else 100

        return sorted_majors[:top_n], max_score

    def _calculate_major_compatibility(self, major: pd.Series, user_profile: Dict[str, Any]) -> Tuple[int, List[str]]:
        score = 0
        reasons = []
        rubric = major['scoring_rubric']

        # Academic Profile
        for subject in user_profile.get('fav_subjects', []):
            if subject in rubric.get('fav_subjects', {}):
                score += rubric['fav_subjects'][subject] * 10
                reasons.append(f"Interest in {subject}")

        # Career Aspirations
        for interest in user_profile.get('job_interest', []):
            if interest in rubric.get('job_interest', {}):
                score += rubric['job_interest'][interest] * 10
                reasons.append(f"Career goal: {interest}")

        # Personal Preferences
        if user_profile.get('work_style') in rubric.get('work_style', {}):
            score += rubric['work_style'][user_profile['work_style']] * 5
        if user_profile.get('company_type') in rubric.get('company_type', {}):
            score += rubric['company_type'][user_profile['company_type']] * 5

        return score, reasons

    def _prepare_features_for_major_recommendation(self, major: pd.Series, user_profile: Dict[str, Any]) -> List[float]:
        """
        Prepares a feature vector for the recommendation model based on user profile and major rubric.
        NOTE: The exact feature engineering should match what the recommendation_model was trained on.
              This is a simplified example.
        """
        features = []
        rubric = major['scoring_rubric']

        # Helper to get score from rubric for a given user preference
        def get_rubric_score(rubric_key, user_value):
            if isinstance(user_value, list):
                return sum(rubric.get(rubric_key, {}).get(item, 0) for item in user_value)
            return rubric.get(rubric_key, {}).get(user_value, 0)

        # Academic Profile features
        features.append(get_rubric_score('fav_subjects', user_profile.get('fav_subjects', [])))

        # Career Aspirations features
        features.append(get_rubric_score('job_interest', user_profile.get('job_interest', [])))

        # Personal Preferences features
        features.append(get_rubric_score('work_style', user_profile.get('work_style')))
        features.append(get_rubric_score('company_type', user_profile.get('company_type')))
        features.append(get_rubric_score('value_priority', user_profile.get('value_priority')))
        features.append(get_rubric_score('social_preference', user_profile.get('social_preference')))
        features.append(get_rubric_score('future_aspiration', user_profile.get('future_aspiration')))
        features.append(get_rubric_score('stress_tolerance', user_profile.get('stress_tolerance')))

        # GPA (numerical mapping)
        gpa_map = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0, "F": 0.0}
        features.append(gpa_map.get(user_profile.get('gpa'), 0.0))

        # Budget (numerical mapping - using midpoint of range)
        budget_str = user_profile.get('budget', '')
        budget_min, budget_max = self._parse_budget(budget_str)
        features.append((budget_min + budget_max) / 2 if budget_min is not None and budget_max is not None else 0.0)

        # English Proficiency (numerical mapping)
        english_proficiency_map = {"Excellent": 3.0, "Medium": 2.0, "Poor": 1.0}
        features.append(english_proficiency_map.get(user_profile.get('english_proficiency'), 0.0))

        # Study Hours (numerical mapping)
        study_hours_str = user_profile.get('study_hours', '')
        if 'ច្រើនជាង' in study_hours_str: # "Above 30"
            features.append(35.0) # Arbitrary high value
        elif '-' in study_hours_str: # "20-30"
            parts = study_hours_str.split('-')
            try:
                features.append((float(parts[0]) + float(parts[1])) / 2)
            except ValueError:
                features.append(0.0)
        else:
            try:
                features.append(float(study_hours_str))
            except ValueError:
                features.append(0.0)

        # Add study_format (numerical mapping)
        study_format_map = {
            "Lecture-based": 1.0,
            "Practical/Hands-on": 2.0,
            "Group work": 3.0,
            "Research-focused": 4.0,
        }
        features.append(study_format_map.get(user_profile.get('study_format'), 0.0))

        # Add location (numerical mapping)
        location_map = {
            "Phnom Penh": 1.0,
            "Siem Reap": 2.0,
            "Battambang": 3.0,
            "Kampong Cham": 4.0,
            "Other Provinces": 5.0,
        }
        features.append(location_map.get(user_profile.get('location'), 0.0))

        return features

    def get_university_recommendations(self, major_name_en: str, user_profile: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Recommends universities for a given major, based on a holistic score.
        """
        major_category = self.major_profiles[self.major_profiles['major_name_en'] == major_name_en].iloc[0]['major_category']

        eligible_universities = self.universities[
            self.universities['major_categories_en'].apply(lambda cats: major_category in cats)
        ]

        if eligible_universities.empty:
            return []

        scores = []
        for index, uni in eligible_universities.iterrows():
            score, reasons = self._calculate_university_compatibility(uni, user_profile, major_category)
            scores.append({
                "university_name": uni['name_en'],
                "score": score,
                "details": ", ".join(reasons)
            })

        return sorted(scores, key=lambda x: x["score"], reverse=True)[:top_n]

    def _calculate_university_compatibility(self, uni: pd.Series, user_profile: Dict[str, Any], major_category: str) -> Tuple[int, List[str]]:
        score = 0
        reasons = []

        # Program Strength (give this a heavy weight)
        if major_category in uni['major_categories_en']:
            score += 100  # Base score for offering the major
            reasons.append(f"Strong in {major_category}")

        # Specialist Bonus
        if uni.get('specialist_in_major_category') == major_category:
            score += 50  # Significant bonus for specialization
            reasons.append(f"Specialist in {major_category}")

        # Ranking Score (use as a tie-breaker)
        score += uni.get('ranking_score', 0) * 0.5  # Reduced weight
        reasons.append(f"University Rank ({uni.get('ranking_score', 0)})")

        # Financial Fit
        user_budget_min, user_budget_max = self._parse_budget(user_profile.get('budget', ""))
        if user_budget_min is not None:
            tuition = uni['tuition_fees']
            if self._is_budget_compatible(tuition, user_budget_min, user_budget_max):
                score += 20
                reasons.append("Fits budget")

        # Location Fit
        if user_profile.get('location') == uni.get('location'):
            score += 15
            reasons.append("Preferred location")

        return score, reasons

    def _parse_budget(self, budget_str: str) -> Tuple[Optional[int], Optional[int]]:
        if not budget_str: return None, None
        parts = budget_str.replace("$", "").replace(",", "").split("-")
        try:
            if len(parts) == 1:
                return int(parts[0]), int(parts[0])
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return None, None

    def _is_budget_compatible(self, uni_fees: Dict, user_min: int, user_max: int) -> bool:
        if not uni_fees or uni_fees.get("range_min") is None: return False
        return max(user_min, uni_fees["range_min"]) <= min(user_max, uni_fees["range_max"]) 

    def add_feedback(self, user_id: int, profile: Dict, major_name: str, feedback: int):
        feedback_record = {
            "feedback_id": str(datetime.datetime.now().timestamp()),
            "user_id": user_id,
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "major_name": major_name,
            "feedback": feedback,
            "user_profile": profile,
        }
        feedback_file = "data/feedback.jsonl"
        try:
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_record, ensure_ascii=False) + "\n")
            logger.info(f"Successfully recorded feedback for user {user_id} on major '{major_name}'.")
        except IOError as e:
            logger.error(f"Failed to write feedback to {feedback_file}: {e}")
