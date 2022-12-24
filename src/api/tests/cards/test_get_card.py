"""
Test Cases
* `get /cards/{card_id}` empty database
* `get /cards/{card_id}` one card database
* `get /cards/{card_id}` many card database
"""
import pytest
from fastapi import status
from api.cards.models import Card, State, Priority

pytestmark = pytest.mark.anyio


@pytest.mark.num_cards(0)
async def test_get_no_ticket(client, clean_db):
    response = await client.get("/api/cards/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.num_cards(0)
async def test_get_ticket_from_one(client, clean_db):
    card = Card(title="test", summary="test summary", state=State.TODO, priority=Priority.LOW)
    await card.save()

    response = await client.get(f"/api/cards/{card.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert card.id == data["id"]
    assert card.summary == data["summary"]
    assert card.state.value == data["state"]
    assert card.priority.value == data["priority"]


@pytest.mark.num_cards(5)
async def test_get_ticket_from_many(client, clean_db):
    card = Card(title="test", summary="test summary", state=State.TODO, priority=Priority.LOW)
    await card.save()

    response = await client.get(f"/api/cards/{card.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert card.id == data["id"]
    assert card.summary == data["summary"]
    assert card.state.value == data["state"]
    assert card.priority.value == data["priority"]

