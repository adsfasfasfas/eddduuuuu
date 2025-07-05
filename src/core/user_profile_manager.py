from tinydb import TinyDB, Query

db = TinyDB('data/user_profiles.json')
User = Query()

def save_user_profile(user_id: int, profile_data: dict):
    """Saves or updates a user's profile."""
    db.upsert({'user_id': user_id, 'profile': profile_data}, User.user_id == user_id)

def get_user_profile(user_id: int) -> dict | None:
    """Retrieves a user's profile."""
    result = db.search(User.user_id == user_id)
    return result[0] if result else None
