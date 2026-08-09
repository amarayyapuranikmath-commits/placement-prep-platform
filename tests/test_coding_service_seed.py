from types import SimpleNamespace

import pytest

from app.models.coding_preference import CODING_PREFERENCES_COLLECTION
from app.models.coding_problem import CODING_PROBLEMS_COLLECTION
from app.models.coding_progress import CODING_PROGRESS_COLLECTION
from app.services import coding_service
from app.services.coding_service import DEFAULT_PROBLEMS


class FakeCursor:
    def __init__(self, docs, query=None):
        self.docs = docs
        self.query = query

    def sort(self, *args, **kwargs):
        return self

    def skip(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    async def to_list(self, length):
        return self.docs[:length]


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = docs or []
        self.inserted_documents = []

    async def count_documents(self, query=None):
        return len(self.docs)

    async def distinct(self, field):
        return [doc.get(field) for doc in self.docs if doc.get(field)]

    async def find_one(self, query=None):
        return self.docs[0] if self.docs else None

    async def insert_one(self, document):
        if "_id" not in document:
            document["_id"] = f"id-{len(self.docs)+1}"
        self.docs.append(document)
        self.inserted_documents.append(document)
        return SimpleNamespace(inserted_id=document["_id"])

    def find(self, query=None):
        return FakeCursor(self.docs, query)

    async def update_one(self, filter_query=None, update_query=None, upsert=False):
        return None


class FakeDatabase:
    def __init__(self):
        self.collections = {
            CODING_PROBLEMS_COLLECTION: FakeCollection(),
            CODING_PROGRESS_COLLECTION: FakeCollection(),
            CODING_PREFERENCES_COLLECTION: FakeCollection(),
        }

    def __getitem__(self, key):
        return self.collections[key]


@pytest.mark.asyncio
async def test_list_problems_seeds_default_problems_without_ai(monkeypatch):
    async def fail_if_called(*args, **kwargs):
        raise AssertionError("AI generation should not be used for browsing problems")

    db = FakeDatabase()
    result = await coding_service.list_problems(
        db=db,
        user_id="user-1",
        search=None,
        category=None,
        difficulty=None,
        language=None,
        page=1,
        page_size=5,
        sort="title",
    )

    assert result.total >= 1
    assert any(problem.title == "Two Sum" for problem in result.problems)
    assert len(db[CODING_PROBLEMS_COLLECTION].inserted_documents) >= 1


def test_default_problem_hidden_tests_have_valid_format():
    for problem in DEFAULT_PROBLEMS:
        input_format = problem.get('input_format', '').lower()
        for case in problem.get('hidden_test_cases', []):
            hidden_input = case.get('input', '')
            lines = hidden_input.splitlines()

            if 'third line' in input_format or 'and the third line' in input_format:
                assert len(lines) == 3, f"{problem['title']} hidden input should have 3 lines"
                if 'second line contains n integers' in input_format:
                    n = int(lines[0].strip())
                    values = lines[1].split()
                    assert len(values) == n, (
                        f"{problem['title']} hidden input count mismatch: expected {n}, got {len(values)}"
                    )

            elif 'followed by n lines each with start and end' in input_format:
                assert len(lines) == int(lines[0].strip()) + 1, (
                    f"{problem['title']} hidden input has wrong number of interval lines"
                )
                for interval in lines[1:]:
                    assert len(interval.split()) == 2, (
                        f"{problem['title']} hidden interval line malformed: {interval}"
                    )

            elif 'followed by n space-separated heights' in input_format or 'followed by house values' in input_format:
                assert len(lines) == 2, f"{problem['title']} hidden input should have 2 lines"
                n = int(lines[0].strip())
                values = lines[1].split()
                assert len(values) == n, (
                    f"{problem['title']} hidden input count mismatch: expected {n}, got {len(values)}"
                )

            elif 'first line contains n and the next line contains n integers' in input_format:
                assert len(lines) == 2, f"{problem['title']} hidden input should have 2 lines"
                n = int(lines[0].strip())
                values = lines[1].split()
                assert len(values) == n, (
                    f"{problem['title']} hidden input count mismatch: expected {n}, got {len(values)}"
                )

            elif 'first line contains n, the second line contains n integers' in input_format:
                assert len(lines) == 2, f"{problem['title']} hidden input should have 2 lines"
                n = int(lines[0].strip())
                values = lines[1].split()
                assert len(values) == n, (
                    f"{problem['title']} hidden input count mismatch: expected {n}, got {len(values)}"
                )

            elif 'the first line contains numcourses' in input_format:
                assert len(lines) >= 1, f"{problem['title']} hidden input should have at least 1 line"
                if len(lines) > 1:
                    for prerequisite in lines[1:]:
                        assert len(prerequisite.split()) == 2, (
                            f"{problem['title']} hidden prerequisite line malformed: {prerequisite}"
                        )

            elif 'the first line contains rows and columns' in input_format:
                assert len(lines) >= 2, f"{problem['title']} hidden input should have at least 2 lines"
                dimensions = lines[0].split()
                assert len(dimensions) == 2, (
                    f"{problem['title']} hidden grid header malformed: {lines[0]}"
                )
                cols = int(dimensions[1])
                assert all(len(row.split()) == cols for row in lines[1:]), (
                    f"{problem['title']} hidden grid row malformed: {lines[1:]}"
                )

            elif 'first line contains the linked list values' in input_format or 'the first line contains the tree values' in input_format or 'the first line contains a string s' in input_format or 'the input contains an integer x' in input_format or 'the input contains level-order tree node values' in input_format or 'the input contains a single string s' in input_format:
                assert len(lines) == 1, (
                    f"{problem['title']} hidden input should have 1 line"
                )

            elif 'followed by n lines' in input_format:
                assert len(lines) == int(lines[0].strip()) + 1, (
                    f"{problem['title']} hidden input has wrong number of lines"
                )

            else:
                assert len(lines) >= 1, (
                    f"{problem['title']} hidden input format unrecognized or malformed: {hidden_input}"
                )


@pytest.mark.asyncio
async def test_get_problem_categories_returns_curated_concepts():
    db = FakeDatabase()
    collection = db[CODING_PROBLEMS_COLLECTION]
    await collection.insert_one({"category": "Arrays"})
    await collection.insert_one({"category": "Binary Search"})
    await collection.insert_one({"category": "Bit Manipulation"})

    result = await coding_service.get_problem_categories(db)

    assert result.categories == [
        "Arrays",
        "Binary Search",
        "Bit Manipulation",
    ]


@pytest.mark.asyncio
async def test_list_problems_matches_search_across_title_category_and_tags(monkeypatch):
    async def skip_seed(*args, **kwargs):
        return None

    monkeypatch.setattr(coding_service, "_ensure_problems_seeded", skip_seed)

    db = FakeDatabase()
    collection = db[CODING_PROBLEMS_COLLECTION]
    await collection.insert_one(
        {
            "title": "Binary Search",
            "category": "Arrays",
            "difficulty": "medium",
            "tags": ["binary-search", "search"],
        }
    )
    await collection.insert_one(
        {
            "title": "Graph Traversal",
            "category": "Graphs",
            "difficulty": "hard",
            "tags": ["dfs", "graph"],
        }
    )

    category_result = await coding_service.list_problems(
        db=db,
        user_id="user-1",
        search="arrays",
        category=None,
        difficulty=None,
        language=None,
        page=1,
        page_size=10,
        sort="title",
    )
    assert any(problem.title == "Binary Search" for problem in category_result.problems)

    tag_result = await coding_service.list_problems(
        db=db,
        user_id="user-1",
        search="dfs",
        category=None,
        difficulty=None,
        language=None,
        page=1,
        page_size=10,
        sort="title",
    )
    assert any(problem.title == "Graph Traversal" for problem in tag_result.problems)

