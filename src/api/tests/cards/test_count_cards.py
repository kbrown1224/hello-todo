"""
Test Cases
* `get /cards/count` empty database
* `get /cards/count` one card database
* `get /cards/count` many card database
"""
import pytest
from fastapi import status
from api.cards.models import Card

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize("n_cards", [0, 1, 5])
async def test_empty_db_count(client, clean_db, n_cards, faker):
    for _ in range(n_cards):
        await Card.objects.create(title=faker.sentence())

    response = await client.get("/api/cards/count/")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["count"] == n_cards
