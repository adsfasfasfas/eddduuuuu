import json
import logging
from src.core.major_profiles import MAJOR_PROFILES

logger = logging.getLogger(__name__)

class UniversityDataManager:
    """Handles loading, processing, and accessing the university data."""

    def __init__(self, data_path: str):
        self._raw_data = []
        self.universities = []
        self._id_map = {}
        self._km_to_en_category_map = self._build_category_map()

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                self._raw_data = json.load(f)
            if self._raw_data:
                self.universities = self._process_universities()
                self._build_id_map()
                logger.info(f"Successfully loaded and processed {len(self.universities)} universities from {data_path}")
        except FileNotFoundError:
            logger.error(f"FATAL ERROR: Data file not found at {data_path}.")
        except json.JSONDecodeError:
            logger.error(f"FATAL ERROR: Could not decode JSON from {data_path}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading data: {e}")

    def _build_category_map(self) -> dict:
        """Builds a mapping from Khmer names to English category names."""
        mapping = {}
        for profile in MAJOR_PROFILES:
            khmer_name = profile.get("major_name_km")
            english_category = profile.get("major_category")
            if khmer_name and english_category:
                mapping[khmer_name] = english_category
        
        # Manual mapping for broader categories
        mapping.update({
            "ធុរកិច្ច": "Business", "គណនេយ្យ": "Business", "ទីផ្សារ": "Business",
            "ហិរញ្ញវត្ថុ និងធនាគារ": "Business", "សេដ្ឋកិច្ច": "Business",
            "ភាសា": "Arts & Humanities", "វិទ្យាសាស្ត្រសង្គម": "Social Sciences",
            "វិស្វកម្ម": "Engineering", "បច្ចេកវិទ្យា": "Technology",
            "វេជ្ជសាស្ត្រ": "Health Sciences", "អប់រំ": "Education"
        })
        return mapping

    def _process_universities(self) -> list:
        """Processes raw data to add structured major and category lists."""
        processed_list = []
        for uni in self._raw_data:
            uni_profile = uni.copy()
            categories_km = set()
            categories_en = set()

            for faculty in uni.get("faculties", []):
                for major in faculty.get("majors", []):
                    category_name_km = major.get("category_km")
                    if category_name_km:
                        categories_km.add(category_name_km)
                        en_category = self._km_to_en_category_map.get(category_name_km)
                        if en_category:
                            categories_en.add(en_category)
            
            uni_profile["major_categories_km"] = list(categories_km)
            uni_profile["major_categories_en"] = list(categories_en)
            processed_list.append(uni_profile)
        return processed_list

    def _build_id_map(self):
        """Creates a fast lookup map from university ID to data."""
        self._id_map = {uni.get("id"): uni for uni in self.universities if uni.get("id")}

    def get_all_universities(self) -> list:
        """Returns the full list of all processed universities."""
        return self.universities

    def get_university_by_id(self, uni_id: int) -> dict | None:
        """Retrieves a single university by its ID."""
        return self._id_map.get(uni_id)

