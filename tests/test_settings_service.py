import pytest
from bson import ObjectId

from app.core.security import hash_password, verify_password
from app.schemas.settings import PasswordUpdateRequest, ProfileUpdateRequest, ThemeUpdateRequest
from app.services import settings_service


@pytest.mark.asyncio
async def test_get_settings_defaults_theme_to_default_for_missing_value():
    user_id = ObjectId()
    user_doc = {
        "_id": user_id,
        "full_name": "User",
        "email": "user@example.com",
        "password_hash": hash_password("OldPass!23"),
    }
    db = FakeDB(user_doc)

    result = await settings_service.get_settings_data(db, str(user_id))

    assert result["theme"] == "default"


class FakeCollection:
    def __init__(self, initial=None):
        self.docs = initial or {}

    async def find_one(self, query):
        if "$or" in query:
            for doc in self.docs.values():
                if any(doc.get(k) == v for k, v in query["$or"]):
                    return doc
            return None
        if "_id" in query:
            return self.docs.get(query["_id"])
        return None

    async def update_one(self, query, update):
        if "_id" in query:
            doc = self.docs[query["_id"]]
            if "$set" in update:
                doc.update(update["$set"])
            return None
        raise AssertionError("unexpected query")


class FakeDB:
    def __init__(self, user_doc):
        self.user_id = user_doc["_id"]
        self.collection = FakeCollection({user_doc["_id"]: user_doc})

    def __getitem__(self, name):
        if name == "users":
            return self.collection
        raise KeyError(name)


@pytest.mark.asyncio
async def test_update_profile_changes_full_name():
    user_id = ObjectId()
    user_doc = {
        "_id": user_id,
        "full_name": "Old Name",
        "email": "user@example.com",
        "password_hash": hash_password("OldPass!23"),
        "theme": "dark",
    }
    db = FakeDB(user_doc)

    result = await settings_service.update_profile(db, str(user_id), ProfileUpdateRequest(full_name="New Name"))

    assert result["full_name"] == "New Name"
    assert result["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_update_password_requires_current_password_and_updates_hash():
    user_id = ObjectId()
    old_hash = hash_password("OldPass!23")
    user_doc = {
        "_id": user_id,
        "full_name": "User",
        "email": "user@example.com",
        "password_hash": old_hash,
        "theme": "dark",
    }
    db = FakeDB(user_doc)

    result = await settings_service.update_password(
        db,
        str(user_id),
        PasswordUpdateRequest(current_password="OldPass!23", new_password="NewPass!23", confirm_password="NewPass!23"),
    )

    assert "password_hash" not in result
    assert result["message"] == "Password updated successfully"


@pytest.mark.asyncio
async def test_update_theme_persists_preference():
    user_id = ObjectId()
    user_doc = {
        "_id": user_id,
        "full_name": "User",
        "email": "user@example.com",
        "password_hash": hash_password("OldPass!23"),
        "theme": "dark",
    }
    db = FakeDB(user_doc)

    result = await settings_service.update_theme(db, str(user_id), ThemeUpdateRequest(theme="light"))

    assert result["theme"] == "light"
