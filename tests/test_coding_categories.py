import pytest

from app.services import coding_service


class DummyCollection:
    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, *args, **kwargs):
        return type("Result", (), {"inserted_id": "1"})()

    async def distinct(self, field):
        return ["Dynamic Programming", "Arrays", "Arrays", "Backtracking"]


class DummyDB:
    def __getitem__(self, name):
        return DummyCollection()


@pytest.mark.asyncio
async def test_get_problem_categories_returns_sorted_unique_categories():
    categories = await coding_service.get_problem_categories(DummyDB())

    assert categories.categories == ["Arrays", "Backtracking", "Dynamic Programming"]
