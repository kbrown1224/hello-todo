"""
Test Cases
* `patch /cards/start/{card_id}` all states
* `patch /cards/start/{card_id}` an invalid id
* `patch /cards/start/{card_id}` many in db
"""
import pytest
from fastapi import status
from api.cards.models import Card, State, Priority

pytestmark = pytest.mark.anyio


@pytest.mark.num_cards(0)
async def test_start_states(client, state_option):
    card = Card(title="Test", state=state_option)
    await card.save()

    response = await client.patch(f"/api/cards/start/{card.id}")
    db_card = await Card.objects.get(id=card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_card.state == State.IN_PROGRESS


@pytest.mark.num_cards(0)
async def test_start_no_card(client):
    response = await client.patch("/api/cards/start/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.num_cards(0)
async def test_start_states(client, state_option):
    card = Card(title="Test", state=state_option)
    other_card_1 = Card(title="Other 1")
    other_card_2 = Card(title="Other 2")
    await card.save()
    await other_card_1.save()
    await other_card_2.save()

    response = await client.patch(f"/api/cards/start/{card.id}")
    db_card = await Card.objects.get(id=card.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db_card.state == State.IN_PROGRESS

    for other_card in [other_card_1, other_card_2]:
        db_other_card = await Card.objects.get(id=other_card.id)
        assert other_card == db_other_card

