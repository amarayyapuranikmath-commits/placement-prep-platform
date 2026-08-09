from pymongo import MongoClient
from app.core.config import get_settings

settings = get_settings()
print("Connecting...")
client = MongoClient(settings.MONGODB_URI)
print(client.admin.command("ping"))
print("Connected Successfully!")