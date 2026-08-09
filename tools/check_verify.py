import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from pymongo import MongoClient
import certifi
from app.core.security import verify_password
from app.core.security import hash_password

settings = get_settings()
client = MongoClient(settings.MONGODB_URI, tls=True, tlsCAFile=certifi.where())
db = client[settings.MONGODB_DB_NAME]
user = db.users.find_one({'email':'test@example.com'})
print('Stored hash:', user.get('password_hash'))
print('Verify:', verify_password('Password1!', user.get('password_hash')))

new_hash = hash_password('Password1!')
print('New hash:', new_hash)
print('Verify new hash:', verify_password('Password1!', new_hash))

from passlib.hash import pbkdf2_sha256 as pl_pbkdf
print('passlib pbkdf2_sha256 verify stored:', pl_pbkdf.verify('Password1!', user.get('password_hash')))
