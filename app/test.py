from pymongo import MongoClient

uri = "PASTE_YOUR_MONGODB_URI_HERE"

client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("✅ Connected successfully!")
except Exception as e:
    print(e)