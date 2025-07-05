
# -*- coding: utf-8 -*-
"""
This file defines the profiles for various academic majors. Each profile is a dictionary
containing a description, a category, and a detailed scoring rubric that maps
quiz answers to scores for that major.
"""

# This is now a LIST of dictionaries, which is the correct format.
MAJOR_PROFILES = [
  {
    "major_name": "បច្ចេកវិទ្យា (Technology)",
    "major_name_en": "Technology",
    "major_name_km": "បច្ចេកវិទ្យា",
    "major_category": "Technology",
    "description": "Focuses on computer science, data analysis, and software development.",
    "scoring_rubric": {
      "fav_subjects": {"Mathematics": 3, "Science": 1, "Language": 1},
      "job_interest": {"Software Developer": 3, "Engineer": 2, "Businessman/woman": 1},
      "work_style": {"Independent": 3, "Team-oriented": 2},
      "company_type": {"Startup": 3, "Private Company": 2},
      "value_priority": {"Career Growth": 3, "High Salary": 2},
      "future_aspiration": {"Expert/Specialist": 2, "Freelancer": 2, "Business Owner/Entrepreneur": 1},
      "stress_tolerance": {"High": 2, "Medium": 1},
      "study_format": {"Practical/Hands-on": 3, "Lecture-based": 1},
      "english_proficiency": {"Excellent": 2, "Medium": 1},
      "gpa": {"A": 2, "B": 1},
      "study_hours": {"20-30": 1, "Above 30": 2}
    }
  },
  {
    "major_name": "វិស្វកម្ម (Engineering)",
    "major_name_en": "Engineering",
    "major_name_km": "វិស្វកម្ម",
    "major_category": "Engineering",
    "description": "Involves designing, building, and maintaining engines, machines, and structures.",
    "scoring_rubric": {
      "fav_subjects": {"Mathematics": 3, "Science": 3},
      "job_interest": {"Engineer": 3, "Software Developer": 1},
      "work_style": {"Team-oriented": 3, "Independent": 1},
      "company_type": {"Private Company": 2, "Government": 1},
      "value_priority": {"Stability": 3, "Career Growth": 2, "High Salary": 1},
      "future_aspiration": {"Expert/Specialist": 3, "Manager/Leader": 1},
      "stress_tolerance": {"High": 2, "Medium": 1},
      "study_format": {"Practical/Hands-on": 3, "Group work": 2},
      "english_proficiency": {"Excellent": 1, "Medium": 1},
      "gpa": {"A": 3, "B": 2, "C": 1},
      "study_hours": {"20-30": 1, "Above 30": 3}
    }
  },
  {
    "major_name": "វេជ្ជសាស្ត្រ (Health Sciences)",
    "major_name_en": "Health Sciences",
    "major_name_km": "វេជ្ជសាស្ត្រ",
    "major_category": "Health Sciences",
    "description": "Covers various disciplines related to health and medical treatment.",
    "scoring_rubric": {
      "fav_subjects": {"Science": 3},
      "job_interest": {"Doctor": 3},
      "work_style": {"Team-oriented": 2, "Independent": 1},
      "company_type": {"Government": 2, "Private Company": 1, "Non-profit": 1},
      "value_priority": {"Stability": 3, "Work-Life Balance": 1},
      "social_preference": {"Highly Social": 2, "Moderately Social": 1},
      "future_aspiration": {"Expert/Specialist": 3},
      "stress_tolerance": {"High": 3, "Medium": 1},
      "study_format": {"Lecture-based": 2, "Group work": 1},
      "english_proficiency": {"Excellent": 2, "Medium": 1},
      "gpa": {"A": 3, "B": 2, "C": 1},
      "study_hours": {"20-30": 2, "Above 30": 3}
    }
  },
  {
    "major_name": "ធុរកិច្ចនិងគ្រប់គ្រង (Business & Management)",
    "major_name_en": "Business & Management",
    "major_name_km": "ធុរកិច្ចនិងគ្រប់គ្រង",
    "major_category": "Business",
    "description": "Prepares for careers in business, finance, and management.",
    "scoring_rubric": {
      "fav_subjects": {"Social Studies": 2, "Language": 1},
      "job_interest": {"Businessman/woman": 3, "Marketer": 2, "Manager": 2},
      "work_style": {"Leadership": 3, "Team-oriented": 2},
      "company_type": {"Private Company": 3, "Startup": 2},
      "value_priority": {"High Salary": 3, "Career Growth": 2},
      "social_preference": {"Highly Social": 3, "Moderately Social": 1},
      "future_aspiration": {"Business Owner/Entrepreneur": 3, "Manager/Leader": 3},
      "stress_tolerance": {"High": 1, "Medium": 1},
      "study_format": {"Group work": 3, "Lecture-based": 1},
      "english_proficiency": {"Excellent": 2, "Medium": 1},
      "gpa": {"A": 1, "B": 1}
    }
  },
  {
    "major_name": "សិល្បៈនិងមនុស្សសាស្ត្រ (Arts & Humanities)",
    "major_name_en": "Arts & Humanities",
    "major_name_km": "សិល្បៈនិងមនុស្សសាស្ត្រ",
    "major_category": "Arts",
    "description": "Explores human culture, expression, and history.",
    "scoring_rubric": {
      "fav_subjects": {"Arts": 3, "Language": 2, "Social Studies": 1},
      "job_interest": {"Artist": 3, "Teacher": 1},
      "work_style": {"Independent": 3, "Supportive": 1},
      "company_type": {"Non-profit": 2, "Freelancer": 2},
      "value_priority": {"Work-Life Balance": 3},
      "social_preference": {"Less Social": 2, "Moderately Social": 1},
      "future_aspiration": {"Freelancer": 3, "Expert/Specialist": 1},
      "stress_tolerance": {"Medium": 1, "Low": 1},
      "study_format": {"Lecture-based": 2, "Practical/Hands-on": 1},
      "gpa": {"A": 1, "B": 1, "C": 1, "D": 1, "E": 1}
    }
  },
  {
    "major_name": "វិទ្យាសាស្ត្រសង្គម (Social Sciences)",
    "major_name_en": "Social Sciences",
    "major_name_km": "វិទ្យាសាស្ត្រសង្គម",
    "major_category": "Social Sciences",
    "description": "Studies society and the relationships among individuals within a society.",
    "scoring_rubric": {
      "fav_subjects": {"Social Studies": 3, "Language": 1},
      "job_interest": {"Teacher": 2, "Businessman/woman": 1},
      "work_style": {"Supportive": 2, "Team-oriented": 1, "Independent": 1},
      "company_type": {"Government": 3, "Non-profit": 2},
      "value_priority": {"Work-Life Balance": 2, "Stability": 1},
      "social_preference": {"Highly Social": 2, "Moderately Social": 1},
      "future_aspiration": {"Expert/Specialist": 2, "Manager/Leader": 1},
      "stress_tolerance": {"Medium": 2, "High": 1},
      "study_format": {"Lecture-based": 3, "Group work": 1},
      "gpa": {"A": 1, "B": 1, "C": 1}
    }
  },
  {
    "major_name": "អប់រំ (Education)",
    "major_name_en": "Education",
    "major_name_km": "អប់រំ",
    "major_category": "Education",
    "description": "Prepares students for careers in education, curriculum development, and administration.",
    "scoring_rubric": {
      "fav_subjects": {"Language": 3, "Social Studies": 3, "Arts": 1},
      "job_interest": {"Teacher": 5, "Manager": 2},
      "work_style": {"Team-oriented": 3, "Leadership": 2},
      "value_priority": {"Work-Life Balance": 3, "Stability": 2},
      "social_preference": {"Highly Social": 2, "Moderately Social": 1},
      "future_aspiration": {"Expert/Specialist": 3, "Manager/Leader": 2},
      "stress_tolerance": {"Medium": 2, "High": 1}
    }
  },
    {
    "major_name": "ទីផ្សារ (Marketing)",
    "major_name_en": "Marketing",
    "major_name_km": "ទីផ្សារ",
    "major_category": "Business",
    "description": "Focuses on promoting and selling products or services, including market research and advertising.",
    "scoring_rubric": {
      "fav_subjects": {"Arts": 2, "Language": 2, "Social Studies": 1},
      "job_interest": {"Marketer": 3, "Businessman/woman": 2, "Artist": 1},
      "work_style": {"Team-oriented": 3, "Leadership": 2, "Independent": 1},
      "company_type": {"Private Company": 3, "Startup": 2},
      "value_priority": {"High Salary": 2, "Career Growth": 2, "Work-Life Balance": 1},
      "social_preference": {"Highly Social": 3, "Moderately Social": 1},
      "future_aspiration": {"Manager/Leader": 2, "Business Owner/Entrepreneur": 2, "Freelancer": 1},
      "stress_tolerance": {"High": 2, "Medium": 1},
      "study_format": {"Group work": 3, "Practical/Hands-on": 1},
      "english_proficiency": {"High": 2, "Medium": 1},
      "gpa": {"A": 1, "B": 1}
    }
  }
]

def load_major_profiles():
    """Returns the list of major profiles."""
    return MAJOR_PROFILES 