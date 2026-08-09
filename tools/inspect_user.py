import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from pymongo import MongoClient
import certifi

settings = get_settings()
uri = settings.MONGODB_URI
print('Using MONGODB_URI:', (uri[:50] + '...') if uri else 'None')

client = MongoClient(uri, tls=True, tlsCAFile=certifi.where())
db = client[settings.MONGODB_DB_NAME]
user = db.users.find_one({'email': 'test@example.com'})
print('User doc:', user)
