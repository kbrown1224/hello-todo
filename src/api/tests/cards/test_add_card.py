"""
Test Cases
* `post /cards/` to an empty database
* `post /cards/` to a non-empty database
* `post /cards/` a card with a missing data
* `post /cards/` a card of each initial state
* `post /cards/` a duplicate card
* `post /cards/` with default values
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from api.cards.models import Card, State, Priority

pytestmark = pytest.mark.anyio


async def test_root(client):
    response = await client.get("/api/db/path")
    assert response.json() == "sqlite:///test_db.sqlite"


@pytest.mark.num_cards(0)
async def test_create_card_empty_db(client: AsyncClient, clean_db, faker, state_option, priority_option):
    body = {
        "title": "test title",
        "summary": "test summary",
        "state": state_option.value,
        'priority': priority_option.value
    }

    response = await client.post("/api/cards/", json=body)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    db_card = await Card.objects.get(id=data["id"])

    assert db_card.title == body["title"]
    assert db_card.summary == body["summary"]
    assert db_card.state.value == body["state"]
    assert db_card.priority.value == body["priority"]

    if db_card.state == State.TODO:
        assert db_card.started_dttm is None

    if db_card.state < State.DONE:
        assert db_card.finished_dttm is None

    # TODO Figure out created time with freeze time


@pytest.mark.num_cards(5)
async def test_create_card_non_empty_db(client: AsyncClient, clean_db, faker, state_option, priority_option):
    body = {
        "title": "test title",
        "summary": "test summary",
        "state": state_option.value,
        'priority': priority_option.value
    }

    response = await client.post("/api/cards/", json=body)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    db_card = await Card.objects.get(id=data["id"])

    assert db_card.title == body["title"]
    assert db_card.summary == body["summary"]
    assert db_card.state.value == body["state"]
    assert db_card.priority.value == body["priority"]
    if db_card.state == State.TODO:
        assert db_card.started_dttm is None

    if db_card.state < State.DONE:
        assert db_card.finished_dttm is None


async def test_create_invalid_state(client, clean_db):
    body = {
        "title": "test title",
        "summary": "test summary",
        "state": "fake",
        'priority': Priority.LOW.value
    }

    response = await client.post("/api/cards/", json=body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_invalid_priority(client, clean_db):
    body = {
        "title": "test title",
        "summary": "test summary",
        "state": State.TODO.value,
        'priority': 100
    }

    response = await client.post("/api/cards/", json=body)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_card_duplicate_title(client, clean_db):
    duplicate_title = "Duplicate Title"
    existing_card = Card(title=duplicate_title, summary="test")
    await existing_card.save()

    body = {
        "title": duplicate_title,
        "summary": "test summary"
    }

    response = await client.post("/api/cards/", json=body)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert existing_card.id != data["id"]
    assert existing_card.title == data["title"]


async def test_default_values(client, clean_db):
    body = {
        "title": "test title",
        "summary": "test summary"
    }

    response = await client.post("/api/cards/", json=body)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["priority"] == Priority.LOW.value
    assert data["state"] == State.TODO.value
