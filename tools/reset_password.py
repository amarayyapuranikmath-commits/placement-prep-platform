import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from pymongo import MongoClient
import certifi
from app.core.security import hash_password

settings = get_settings()
client = MongoClient(settings.MONGODB_URI, tls=True, tlsCAFile=certifi.where())
db = client[settings.MONGODB_DB_NAME]

email = 'test@example.com'
new_pw = 'Password1!'
new_hash = hash_password(new_pw)
result = db.users.update_one({'email': email}, {'$set': {'password_hash': new_hash}})
print('matched:', result.matched_count, 'modified:', result.modified_count)
print('New hash:', new_hash)
